from __future__ import annotations


def test_broker_readiness_endpoint_returns_blocked_default_state() -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get("/api/broker/readiness")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"data", "meta"}
    assert body["data"]["status"] == "blocked"
    assert body["data"]["ready_for_manual_pilot"] is False
    assert "模拟运行天数不足" in body["data"]["failed_reasons"]
    assert "通知渠道未启用" in body["data"]["failed_reasons"]
    assert body["data"]["allowed_actions"] == [
        "read_account",
        "read_positions",
        "read_orders",
    ]
    assert "place_order" not in body["data"]["allowed_actions"]
    assert "不是实盘交易入口" in body["data"]["trade_boundary"]
    assert body["meta"]["request_id"] == "local-dev"


def test_broker_readiness_endpoint_allows_manual_pilot_review_when_checks_pass() -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get(
        "/api/broker/readiness",
        params={
            "simulation_days": 90,
            "max_drawdown": 0.10,
            "failed_runs": 0,
            "notifications_enabled": True,
            "manual_approval_enabled": True,
            "paper_trading_verified": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "manual_pilot_review"
    assert body["data"]["ready_for_manual_pilot"] is True
    assert body["data"]["failed_reasons"] == []
    assert body["data"]["allowed_actions"] == [
        "read_account",
        "read_positions",
        "read_orders",
    ]
    assert body["data"]["trade_boundary"] == "不是实盘交易入口，仅用于人工小资金试点评审。"


def test_broker_readiness_endpoint_validates_numeric_inputs() -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get("/api/broker/readiness", params={"simulation_days": -1})

    assert response.status_code == 422
