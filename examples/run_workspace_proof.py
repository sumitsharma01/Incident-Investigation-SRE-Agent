"""Prove persistence and recovery against real requests with constant offered load."""
import argparse
import json
import time
from pathlib import Path
import httpx

OUT=Path(__file__).resolve().parents[1]/'docs/case-studies/worker-capacity'


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')


def main(backend):
    with httpx.Client(base_url='http://127.0.0.1:8010',timeout=150) as api:
        query = 'label_replace(sum(rate(sre_lab_requests_total{service="checkout-lab"}[30s])), "signal", "traffic_rps", "", "") or label_replace(sre_lab_latency_seconds{service="checkout-lab",quantile="0.95"}, "signal", "p95_seconds", "", "") or label_replace(sre_lab_queue_depth{service="checkout-lab"}, "signal", "queue_depth", "", "")'
        request={'service':'checkout-lab','backend':backend,'description':
            'A single read-only metrics check for checkout-lab. Use only query_grafana_metrics; no discovery, plan, shell or write tools. '
            'Pass this exact PromQL in metric_name and omit service_name: '+query+
            '. Report the observed traffic, P95 and queue, uncertainties and safe next checks. No remediation.'}
        r=api.post('/investigate',json=request);r.raise_for_status();result=r.json()
        save('investigation',result);print('Saved investigation',result['status'],flush=True)
        identifier=result['incident_id']
        before=api.post(f'/incidents/{identifier}/observations',json={'label':'before'});before.raise_for_status()
        save('before',before.json())
        print('Before captured. Restart API now with the same database; proof resumes in 40 seconds.',flush=True)
        time.sleep(40)
        record=api.get('/incidents/'+identifier);record.raise_for_status()
        assert record.json()['result']==result
        assert record.json()['observations'][0]['id']==before.json()['id']
        save('restart-check',{'same_investigation':True,'same_result':True,'same_evidence':True,'incident_id':identifier})
        intervention=httpx.post('http://127.0.0.1:9201/capacity',json={'workers':16},timeout=5)
        intervention.raise_for_status();save('intervention',intervention.json())
        print('Actual service capacity changed 2 → 16; offered load continues. Waiting 40 seconds.',flush=True)
        time.sleep(40)
        after=api.post(f'/incidents/{identifier}/observations',json={'label':'after'});after.raise_for_status();save('after',after.json())
        verification=api.post(f'/incidents/{identifier}/recovery',json={
            'before_id':before.json()['id'],'after_id':after.json()['id'],
            'intervention':'Operator increased local checkout-lab worker capacity from 2 to 16 while offered load remained 50 requests/second.',
            'minimum_traffic_rps':40})
        verification.raise_for_status();save('verification',verification.json())
        save('workspace-record',api.get('/incidents/'+identifier).json())
        print('Recovery verdict:',verification.json()['status'],flush=True)
        assert verification.json()['status']=='recovered'


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--backend',choices=['opensre','demo'],default='opensre')
    main(parser.parse_args().backend)
