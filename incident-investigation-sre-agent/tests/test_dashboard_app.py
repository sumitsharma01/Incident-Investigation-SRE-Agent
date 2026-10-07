from fastapi.testclient import TestClient

from examples.dashboard_app import app


client = TestClient(app)


def test_dashboard_app_renders_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Incident Investigation SRE Agent Dashboard" in response.text
    assert "Error budget remaining" in response.text
    assert "v0.2.0" in response.text
    assert "All values on this page are synthetic" in response.text
