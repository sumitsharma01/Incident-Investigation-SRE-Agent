"""Capture the real Grafana/Prometheus UI while the synthetic peak is active."""
import argparse
import base64
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import httpx
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

RATE = 'sum(rate(sre_demo_requests_total{job="checkout-demo"}[30s]))'
ERRORS = '100 * sum(rate(sre_demo_requests_total{job="checkout-demo",status="500"}[30s])) / ' + RATE


def main(executable: str | None) -> None:
    root = Path(__file__).resolve().parents[1]
    password = dotenv_values(root / '.env.observability').get('SRE_DEMO_GRAFANA_ADMIN_PASSWORD')
    if not password:
        raise SystemExit('Local Grafana password is missing.')
    with httpx.Client(base_url='http://127.0.0.1:9090/', timeout=15) as client:
        for attempt in range(90):
            response = client.get('api/v1/query', params={'query':RATE})
            response.raise_for_status()
            results = response.json().get('data', {}).get('result', [])
            if results and float(results[0]['value'][1]) >= 1450:
                sample_time = float(results[0]['value'][0])
                break
            time.sleep(2)
        else:
            raise SystemExit('Peak did not reach 1,450 req/s. Restart the high-traffic exporter and retry.')
        observed = {}
        for label, query in [('request_rate', RATE), ('error_percent', ERRORS),
                             ('latency_seconds', 'sre_demo_latency_seconds{job="checkout-demo"}'),
                             ('peak_active', 'sre_demo_peak_active{job="checkout-demo"}')]:
            values = client.get('api/v1/query', params={'query':query, 'time':sample_time}).json()['data']['result']
            if not values:
                raise SystemExit('Missing live samples: '+label)
            observed[label] = float(values[0]['value'][1])
        if observed['peak_active'] != 1:
            raise SystemExit('Peak ended before capture. Restart the scenario.')
    output = root / 'docs' / 'screenshots'
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable)
        try:
            headers = {'Authorization':'Basic '+base64.b64encode(('admin:'+password).encode()).decode()}
            ctx = browser.new_context(viewport={'width':1600,'height':1200}, extra_http_headers=headers)
            page = ctx.new_page()
            window = urlencode({'orgId':1, 'from':int((sample_time-300)*1000), 'to':int(sample_time*1000)})
            page.goto('http://127.0.0.1:3000/d/sre-high-traffic?'+window,wait_until='domcontentloaded')
            page.get_by_text('Current request rate', exact=True).wait_for(timeout=30000)
            page.wait_for_timeout(5000)
            page.screenshot(path=str(output / 'grafana-peak-traffic.png'), full_page=True)
            ctx.close()
            page = browser.new_page(viewport={'width':1600,'height':1100})
            params = {'g0.expr':RATE,'g0.tab':'1','g1.expr':ERRORS,'g1.tab':'1',
                      'g2.expr':'sre_demo_latency_seconds{job="checkout-demo"}','g2.tab':'1',
                      'g3.expr':'sre_demo_peak_active{job="checkout-demo"}','g3.tab':'1'}
            sample_end = datetime.fromtimestamp(sample_time, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            params.update({f'g{i}.end_input':sample_end for i in range(4)})
            page.goto('http://127.0.0.1:9090/query?'+urlencode(params),wait_until='domcontentloaded')
            page.get_by_text(re.compile(r'1[45]\d{2}(?:\.\d+)?'), exact=False).first.wait_for(timeout=30000)
            page.screenshot(path=str(output / 'prometheus-peak-traffic.png'), full_page=True)
        finally:
            browser.close()
    report = {'captured_at':datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),
              'sample_time':datetime.fromtimestamp(sample_time, ZoneInfo('Europe/Berlin')).isoformat(),
              'scenario':'synthetic high-traffic lab; no production requests generated',
              'baseline_request_rate':47, 'observed':observed, 'rate_query':RATE}
    (root / 'docs' / 'peak-traffic-observations.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--executable-path')
    args = parser.parse_args()
    main(args.executable_path)
