"""Capture real local Grafana/Prometheus pages after confirming live samples exist."""
import argparse
import base64
from pathlib import Path
from urllib.parse import urlencode

import httpx
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright


def capture(executable_path: str | None = None) -> None:
    root = Path(__file__).resolve().parents[1]
    password = dotenv_values(root / '.env.observability').get('SRE_DEMO_GRAFANA_ADMIN_PASSWORD')
    if not password:
        raise SystemExit('Create .env.observability and start the local demo first.')
    with httpx.Client(base_url='http://127.0.0.1:9090/', timeout=20) as client:
        for query in ['sre_demo_latency_seconds', 'sum(rate(sre_demo_requests_total[1m]))']:
            response = client.get('api/v1/query', params={'query':query})
            response.raise_for_status()
            if not response.json().get('data', {}).get('result'):
                raise SystemExit('No live samples for '+query+'. Wait for scraping or repair the lab; no screenshot was captured.')
    output = root / 'docs' / 'screenshots'
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable_path)
        try:
            headers = {'Authorization':'Basic '+base64.b64encode(('admin:'+password).encode()).decode()}
            context = browser.new_context(viewport={'width':1440,'height':900}, extra_http_headers=headers)
            page = context.new_page()
            page.goto('http://127.0.0.1:3000/d/sre-checkout-demo?orgId=1&from=now-5m&to=now',wait_until='networkidle')
            page.get_by_text('Synthetic p95 latency', exact=True).wait_for(timeout=30000)
            page.wait_for_timeout(5000)
            page.screenshot(path=str(output/'grafana-prometheus-demo.png'), full_page=True)
            context.close()
            page = browser.new_page(viewport={'width':1440,'height':1000})
            query = urlencode({'g0.expr':'sre_demo_latency_seconds{service="checkout"}', 'g0.tab':'1', 'g1.expr':'sum(rate(sre_demo_requests_total[1m]))', 'g1.tab':'1', 'g2.expr':'up{job="checkout-demo"}', 'g2.tab':'1'})
            page.goto('http://127.0.0.1:9090/query?'+query,wait_until='domcontentloaded')
            page.get_by_text('0.42', exact=False).first.wait_for(timeout=30000)
            page.screenshot(path=str(output/'prometheus-demo-query.png'), full_page=True)
        finally:
            browser.close()
    print('Captured Grafana dashboard and Prometheus query. Inspect both images before publishing.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--executable-path')
    args = parser.parse_args()
    capture(args.executable_path)
