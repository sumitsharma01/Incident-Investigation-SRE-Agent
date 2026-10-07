"""Create a Viewer token for the loopback-only demo Grafana; never print secrets."""
import time
from pathlib import Path
from dotenv import dotenv_values
import httpx
root=Path(__file__).resolve().parents[1]
password=dotenv_values(root/'.env.observability')['SRE_DEMO_GRAFANA_ADMIN_PASSWORD']
with httpx.Client(base_url='http://127.0.0.1:3000/',auth=('admin',password),timeout=10) as c:
 for attempt in range(30):
  try:
   r=c.get('api/health')
   if r.status_code==200:break
  except httpx.HTTPError:pass
  time.sleep(2)
 else:raise SystemExit('Grafana did not become ready')
 r=c.post('api/serviceaccounts',json={'name':'sre-agent-demo-reader','role':'Viewer'})
 if r.status_code in (200,201):
  account=r.json()['id']
 else:
  existing=c.get('api/serviceaccounts/search',params={'query':'sre-agent-demo-reader'});existing.raise_for_status()
  accounts=[a for a in existing.json().get('serviceAccounts',[]) if a.get('name')=='sre-agent-demo-reader' and a.get('role')=='Viewer']
  if not accounts:raise SystemExit('Service account creation failed: HTTP '+str(r.status_code))
  account=accounts[0]['id']
 r=c.post(f'api/serviceaccounts/{account}/tokens',json={'name':'sre-agent-local-demo','secondsToLive':604800})
 if r.status_code not in (200,201):raise SystemExit('Token creation failed: HTTP '+str(r.status_code))
 token=r.json()['key']
 values={'GRAFANA_INSTANCE_URL':'http://127.0.0.1:3000','GRAFANA_READ_TOKEN':token,'GRAFANA_VERIFY_SSL':'true','GRAFANA_MIMIR_DATASOURCE_UID':'sre-demo-prometheus'}
 p=root/'.env';lines=p.read_text().splitlines();lines=[l for l in lines if l.partition('=')[0] not in values];lines += [k+'='+v for k,v in values.items()];p.write_text('\n'.join(lines)+'\n');p.chmod(0o600)
 print('Saved local Grafana Viewer token (expires in 7 days) and Prometheus datasource configuration.')
