"""Record the overload lab through the actual HTTP API; retain evidence for review."""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'case-studies' / 'checkout-overload'
RATE = 'sum(rate(sre_demo_requests_total{job="checkout-demo"}[30s]))'
QUERIES = {
    'incoming_rps': RATE,
    'successful_rps': 'sum(rate(sre_demo_requests_total{job="checkout-demo",status="200"}[30s]))',
    'error_percent': '100 * sum(rate(sre_demo_requests_total{job="checkout-demo",status="500"}[30s])) / '+RATE,
    'p95_seconds': 'sre_demo_latency_seconds{job="checkout-demo"}',
    'queue_depth': 'sre_demo_queue_depth{job="checkout-demo"}',
    'worker_utilization': 'sre_demo_worker_utilization{job="checkout-demo"}',
    'rejected_rps': 'sum(rate(sre_demo_admission_rejections_total{job="checkout-demo"}[30s]))',
    'phase': 'sre_demo_incident_phase{job="checkout-demo"}',
}


def snapshot(client: httpx.Client) -> dict:
    phase = client.get('api/v1/query', params={'query':QUERIES['phase']})
    phase.raise_for_status()
    rows = phase.json()['data']['result']
    if not rows:
        return {}
    stamp = float(rows[0]['value'][0])
    values = {}
    for name, query in QUERIES.items():
        r = client.get('api/v1/query', params={'query':query, 'time':stamp})
        r.raise_for_status()
        rows = r.json()['data']['result']
        if not rows:
            return {}
        values[name] = float(rows[0]['value'][1])
    return {'timestamp':stamp, 'time_berlin':datetime.fromtimestamp(stamp, ZoneInfo('Europe/Berlin')).isoformat(),
            'values':values, 'queries':QUERIES}


def wait_phase(client: httpx.Client, phase: int, low: float, high: float) -> dict:
    for attempt in range(180):
        sample = snapshot(client)
        if sample and sample['values']['phase'] == phase and low <= sample['values']['incoming_rps'] <= high:
            return sample
        time.sleep(2)
    raise RuntimeError('Expected phase was not observed; restart the overload exporter and rerun.')


def save(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, indent=2)+'\n')


def main(api_url: str) -> None:
    with httpx.Client(base_url='http://127.0.0.1:9090/', timeout=15) as prometheus:
        baseline = wait_phase(prometheus, 0, 195, 205)
        # Avoid first scrape/reset artifacts; keep a useful baseline history.
        time.sleep(15)
        baseline = snapshot(prometheus)
        if baseline['values']['phase'] != 0:
            raise RuntimeError('Baseline elapsed before recording; restart and rerun.')
        save('baseline.json', baseline)
        print('Recorded baseline', flush=True)
        incident = wait_phase(prometheus, 1, 1950, 2050)
        save('incident.json', incident)
        print('Recorded overload incident', flush=True)
        stamp = incident['timestamp']
        query = (
            'label_replace(sum(rate(sre_demo_requests_total{job="checkout-demo"}[30s] @ '+str(stamp)+')), "signal", "incoming_rps", "", "") or '
            'label_replace(sre_demo_latency_seconds{job="checkout-demo"} @ '+str(stamp)+', "signal", "p95_seconds", "", "") or '
            'label_replace(sre_demo_queue_depth{job="checkout-demo"} @ '+str(stamp)+', "signal", "queue_depth", "", "")'
        )
        request = {'service':'checkout','backend':'opensre','description':
            'A single read-only metrics check for a synthetic local incident. Use only query_grafana_metrics, '
            'no plan tools, alerts, shell or writes. Pass this exact PromQL in metric_name and omit service_name: '+query+
            '. After the tool returns, give a concise standalone report explaining the observed request rate, P95, '
            'and queue depth, the likely saturation pattern, and one safe next debugging step. '
            'Do not acknowledge completion of a plan. Do not claim a proven deployment or dependency cause. '
            'Baseline directly measured by Prometheus: '+json.dumps(baseline['values'])+
            '. Incident error percentage directly measured by Prometheus: '+str(incident['values']['error_percent'])+'.'}
        save('request.json', request)
        with httpx.Client(timeout=300) as api:
            health = api.get(api_url+'/health');health.raise_for_status();save('health.json', health.json())
            started = time.monotonic()
            r = api.post(api_url+'/investigate', json=request);r.raise_for_status()
            agent = r.json();save('agent-response.json', agent)
            print('OpenSRE agent status: '+agent.get('status','unknown'), flush=True)
            save('execution.json', {'api_url':api_url,'http_status':r.status_code,'agent_seconds':round(time.monotonic()-started,2),
                 'synthetic':True,'automatic_remediation':False})
            demo = api.post(api_url+'/investigate',json={'service':'checkout','backend':'demo','description':'Separate synthetic demo-path check: checkout latency increased.'})
            demo.raise_for_status();save('demo-path-response.json',demo.json())
        recovery = wait_phase(prometheus, 2, 1950, 2050)
        # A full rate window after recovery must show errors falling.
        for attempt in range(60):
            recovery = snapshot(prometheus)
            if recovery['values']['error_percent'] < 1: break
            time.sleep(2)
        save('recovery.json', recovery)
        print('Recorded modeled recovery (generator-driven, not agent remediation)', flush=True)
    save('run.json', {'scenario':'checkout overload','synthetic':True,'baseline':baseline,'incident':incident,'recovery':recovery,
         'agent':agent,'components':{'live':['FastAPI HTTP','orchestrator','planner','request-local memory','safety validation','OpenSRE CLI','Azure model','Grafana datasource proxy','Prometheus'],
         'demo_only':['mock log/metric/trace/deployment/history collectors','fixed hypotheses','optional Azure demo summary']}})


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--api-url',default='http://127.0.0.1:8000')
    main(parser.parse_args().api_url)
