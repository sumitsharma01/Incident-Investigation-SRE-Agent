from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.3.0"
    assert app.openapi()["info"]["version"] == "0.3.0"


def test_investigate_endpoint():
    response = client.post(
        "/investigate",
        json={"service": "checkout", "description": "Checkout service latency increased significantly"},
    )

    assert response.status_code == 200
    assert response.json()["service"] == "checkout"
    assert len(response.json()["hypotheses"]) >= 1
