from app.tools.deployments import get_recent_deployments
from app.tools.logs import get_logs
from app.tools.metrics import get_metrics
from app.tools.traces import get_traces
from app.tools.incidents import search_similar_incidents


def test_tools_return_mock_observability_data():
    assert get_logs("checkout", "1h")
    assert get_metrics("checkout")
    assert get_traces("checkout")
    assert get_recent_deployments("checkout")
    assert search_similar_incidents("latency")
