import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.workspace.store import Store
from app.workspace.routes import RecoveryRequest
from app.workspace.metrics import compare, capture, MetricError


@pytest.fixture(autouse=True)
def temporary_db(tmp_path, monkeypatch):
    monkeypatch.setenv('SRE_WORKSPACE_DB', str(tmp_path/'workspace.sqlite3'))


def observation(stamp, traffic=50, p95=.8, errors=.5, queue=30):
    return {'service':'checkout-lab','evaluated_at':stamp,'signals':{
        key: {'value':value,'query':key} for key,value in
        {'traffic_rps':traffic,'p95_seconds':p95,'error_ratio':errors,'queue_depth':queue}.items()}}


def policy():
    return RecoveryRequest(before_id='a',after_id='b',intervention='increase workers')


def test_restart_retains_investigation_and_evidence():
    with TestClient(app) as client:
        response=client.post('/investigate',json={'service':'checkout','description':'rising latency'}).json()
        identifier=response['incident_id']
        evidence=Store().create('observation',observation(100),identifier)
    with TestClient(app) as restarted:
        record=restarted.get('/incidents/'+identifier).json()
        assert record['result']==response
        assert record['observations'][0]['signals']==evidence['signals']
        assert record['state']=='success'


def test_restart_marks_incomplete_not_success():
    pending=Store().create('incident',{'request':{},'state':'running','result':None})
    with TestClient(app) as client:
        assert client.get('/incidents/'+pending['id']).json()['state']=='interrupted'


def test_comparable_recovery_and_traffic_drop():
    before=observation(100)
    after=observation(140,p95=.13,errors=0,queue=0)
    assert compare(before,after,policy())['status']=='recovered'
    assert compare(before,observation(140,traffic=5,p95=.13,errors=0,queue=0),policy())['status']=='inconclusive'
    assert compare(before,observation(120,p95=.13,errors=0,queue=0),policy())['status']=='inconclusive'
    assert compare(before,observation(140,p95=.8,errors=0,queue=0),policy())['status']=='not_recovered'


def test_snapshots_cannot_cross_incidents():
    store=Store()
    first=store.create('incident',{'request':{'service':'checkout-lab'},'state':'success'})
    other=store.create('incident',{'request':{'service':'checkout-lab'},'state':'success'})
    before=store.create('observation',dict(observation(100),label='before'),first['id'])
    after=store.create('observation',dict(observation(140,p95=.13),label='after'),other['id'])
    with TestClient(app) as client:
        response=client.post('/incidents/'+first['id']+'/recovery',json={'before_id':before['id'],'after_id':after['id'],'intervention':'increase workers'})
        assert response.status_code==404


@pytest.mark.parametrize('value', ['NaN','Inf','-1','20'])
def test_capture_rejects_invalid_or_stale_metrics(monkeypatch,value):
    def get(self,url,params):
        v=value if 'timestamp(' in params['query'] else '1'
        return httpx.Response(200,request=httpx.Request('GET',url),json={'status':'success','data':{'resultType':'vector','result':[{'value':[params['time'],v]}]}})
    monkeypatch.setattr(httpx.Client,'get',get)
    with pytest.raises(MetricError):capture('checkout-lab','before')


def test_failed_observation_is_not_persisted(monkeypatch):
    from app.workspace import routes
    record=Store().create('incident',{'request':{'service':'checkout-lab'},'state':'success'})
    def fail(*args):raise MetricError('No series')
    monkeypatch.setattr(routes,'capture',fail)
    with TestClient(app) as client:
        assert client.post('/incidents/'+record['id']+'/observations',json={'label':'before'}).status_code==502
        assert client.get('/incidents/'+record['id']).json()['observations']==[]


def test_tenant_access_and_service_scope(tmp_path,monkeypatch):
    import json
    config=tmp_path/'tenants.json'
    config.write_text(json.dumps({'team-a':{'api_key':'a'*40,'services':['checkout-a']},'team-b':{'api_key':'b'*40,'services':['checkout-b']}}))
    monkeypatch.setenv('SRE_TENANTS_FILE',str(config))
    a={'Authorization':'Bearer '+'a'*40};b={'Authorization':'Bearer '+'b'*40}
    with TestClient(app) as client:
        assert client.get('/incidents').status_code==401
        result=client.post('/investigate',headers=a,json={'service':'checkout-a','description':'latency'}).json()
        identifier=result['incident_id']
        assert client.get('/incidents',headers=b).json()==[]
        assert client.get('/incidents/'+identifier,headers=b).status_code==404
        assert client.post('/incidents/'+identifier+'/observations',headers=b,json={'label':'before'}).status_code==404
        assert client.post('/incidents/'+identifier+'/recovery',headers=b,json={'before_id':'x','after_id':'y','intervention':'fix capacity'}).status_code==404
        assert client.post('/investigate',headers=a,json={'service':'checkout-b','description':'latency'}).status_code==403
        assert client.post('/investigate',headers=a,json={'service':'checkout-a','description':'latency','backend':'opensre'}).status_code==503
    with TestClient(app) as restarted:
        assert restarted.get('/incidents/'+identifier,headers=a).json()['result']==result
        assert restarted.get('/incidents/'+identifier,headers=b).status_code==404


def test_tenant_runtime_does_not_inherit_credentials(monkeypatch,tmp_path):
    import subprocess,json
    from app.agent.opensre import OpenSREBackend
    from app.workspace.tenancy import profile
    monkeypatch.setenv('AZURE_OPENAI_API_KEY','other-tenant-secret')
    monkeypatch.setenv('GRAFANA_READ_TOKEN','other-tenant-token')
    config={'opensre_home':str(tmp_path),'model_env':{'LLM_PROVIDER':'azure-openai','AZURE_OPENAI_API_KEY':'own-secret'}}
    context=profile.set(config)
    captured={}
    def run(*args,**kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(args[0],0,stdout=json.dumps({'status':'success','response':'Evidence reviewed'}))
    monkeypatch.setattr(subprocess,'run',run)
    try:assert OpenSREBackend().investigate('checkout-a','latency').status=='success'
    finally:profile.reset(context)
    assert captured['env']['AZURE_OPENAI_API_KEY']=='own-secret'
    assert 'GRAFANA_READ_TOKEN' not in captured['env']
    assert captured['env']['OPENSRE_HOME']==str(tmp_path)
    assert captured['cwd']==str(tmp_path)
