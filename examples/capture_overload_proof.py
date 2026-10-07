"""Capture the recorded overload windows in Grafana/Prometheus and the agent view."""
import argparse
import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from dotenv import dotenv_values
from playwright.sync_api import sync_playwright


def main(executable: str | None) -> None:
    root=Path(__file__).resolve().parents[1]
    case=root/'docs'/'case-studies'/'checkout-overload'
    data=json.loads((case/'run.json').read_text())
    password=dotenv_values(root/'.env.observability')['SRE_DEMO_GRAFANA_ADMIN_PASSWORD']
    output=case/'screenshots';output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=executable)
        try:
            headers={'Authorization':'Basic '+base64.b64encode(('admin:'+password).encode()).decode()}
            ctx=browser.new_context(viewport={'width':1600,'height':1200},extra_http_headers=headers)
            page=ctx.new_page()
            for phase in ['baseline','incident','recovery']:
                end=data[phase]['timestamp']
                params=urlencode({'orgId':1,'from':int((data['baseline']['timestamp']-15)*1000),'to':int(end*1000)})
                page.goto('http://127.0.0.1:3000/d/sre-overload-proof?'+params,wait_until='domcontentloaded')
                page.get_by_text('Incoming traffic',exact=True).wait_for(timeout=30000)
                page.wait_for_timeout(5000)
                page.screenshot(path=str(output/f'grafana-{phase}.png'),full_page=True)
            ctx.close()
            page=browser.new_page(viewport={'width':1600,'height':1200})
            sample_end=datetime.fromtimestamp(data['incident']['timestamp'],timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
            params={}
            for i,key in enumerate(['incoming_rps','p95_seconds','error_percent','queue_depth']):
                params.update({f'g{i}.expr':data['incident']['queries'][key],f'g{i}.tab':'1',f'g{i}.end_input':sample_end})
            page.goto('http://127.0.0.1:9090/query?'+urlencode(params),wait_until='domcontentloaded')
            page.get_by_text(re.compile(r'2\.4\b'),exact=False).first.wait_for(timeout=30000)
            page.screenshot(path=str(output/'prometheus-incident.png'),full_page=True)
            page=browser.new_page(viewport={'width':1600,'height':1250})
            page.goto('http://127.0.0.1:8001/case-study',wait_until='domcontentloaded')
            page.get_by_text('Agent response · verbatim excerpt',exact=True).wait_for(timeout=30000)
            page.screenshot(path=str(output/'agent-findings.png'),full_page=True)
            page.screenshot(path=str(output/'agent-overview.png'),full_page=False)
            page=browser.new_page(viewport={'width':1440,'height':1000})
            page.goto('http://127.0.0.1:8001/',wait_until='domcontentloaded')
            page.screenshot(path=str(output/'demo-dashboard.png'),full_page=True)
        finally:
            browser.close()
    print('Captured baseline, incident, recovery, query results, agent findings and separate demo dashboard.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--executable-path')
    main(parser.parse_args().executable_path)
