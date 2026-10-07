import httpx
from examples.verify_grafana import verify


def test_query_uses_selected_proxy_without_returning_labels():
    def handler(request):
        if request.url.path == '/api/datasources':
            return httpx.Response(200, json=[{'type':'prometheus','uid':'metrics','name':'Prometheus'}])
        assert request.url.path == '/api/datasources/proxy/uid/metrics/api/v1/query'
        assert request.url.params['query'] == 'up'
        return httpx.Response(200, json={'status':'success','data':{'result':[{'metric':{'private':'label'},'value':[1,'1']}]}})
    with httpx.Client(base_url='https://grafana.example/', transport=httpx.MockTransport(handler)) as client:
        result = verify(client)
    assert result['status'] == 'success'
    assert result['series_count'] == 1
    assert 'private' not in str(result)


def test_multiple_datasources_require_selection():
    with httpx.Client(base_url='https://grafana.example/', transport=httpx.MockTransport(lambda r: httpx.Response(200,json=[{'type':'prometheus','uid':'a'},{'type':'prometheus','uid':'b'}]))) as client:
        assert verify(client)['status'] == 'needs_input'


def test_missing_prometheus_is_not_success():
    with httpx.Client(base_url='https://grafana.example/', transport=httpx.MockTransport(lambda r: httpx.Response(200,json=[]))) as client:
        assert verify(client)['status'] == 'error'
