from fastapi.testclient import TestClient

from examples.dashboard_app import app


client = TestClient(app)


def test_dashboard_app_renders_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Incident Investigation SRE Agent Dashboard" in response.text
    assert "Error budget remaining" in response.text
    assert "v0.4.0" in response.text
    assert "All values on this page are synthetic" in response.text


def test_integration_dashboard_explains_backend_without_live_claims():
    response = client.get("/integration")
    assert response.status_code == 200
    assert "What OpenSRE adds" in response.text
    assert "does not report live connector health" in response.text
    assert "backend: opensre" in response.text
    assert "approval_required" in response.text


def test_case_study_route_is_available():
    response = client.get('/case-study')
    assert response.status_code == 200
    assert 'case study' in response.text.lower() or 'recorded proof run' in response.text.lower()


def test_case_study_escapes_external_agent_text(tmp_path, monkeypatch):
    import json
    from examples import case_study_view
    values={'incoming_rps':2000,'successful_rps':1600,'p95_seconds':2.4,'error_percent':20,'queue_depth':850,'worker_utilization':0.95}
    snapshot={'values':values,'time_berlin':'2026-10-07T13:00:00+02:00'}
    run=tmp_path/'run.json'
    run.write_text(json.dumps({'baseline':snapshot,'incident':snapshot,'recovery':snapshot,'agent':{'status':'success','summary':'<script>alert(1)</script>','investigation_plan':['<img src=x onerror=alert(1)>']}}))
    monkeypatch.setattr(case_study_view,'RUN',run)
    page=case_study_view.render_case_study()
    assert '<script>' not in page
    assert '&lt;script&gt;' in page
    assert '<img src=x' not in page
