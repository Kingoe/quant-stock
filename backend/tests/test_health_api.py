from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_api_convention_response() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"] == {
        "status": "ok",
        "service": "quant-stock-backend",
    }
    assert body["meta"]["request_id"] == "local-dev"
    assert datetime.fromisoformat(body["meta"]["generated_at"])
