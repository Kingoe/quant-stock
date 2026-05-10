from __future__ import annotations

from unittest.mock import patch


def test_run_weekly_strategy_endpoint_creates_success_log(tmp_path) -> None:
    """测试手动运行本周策略端点会记录成功日志。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.portfolio import RebalanceRecommendation
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    mock_recommendations = [
        RebalanceRecommendation(
            stock_code="000001",
            stock_name="平安银行",
            action="buy",
            target_weight=0.08,
            total_score=0.75,
            rank=1,
            reason="新增目标持仓",
            risk_note=None,
        ),
        RebalanceRecommendation(
            stock_code="600000",
            stock_name="浦发银行",
            action="watch",
            target_weight=None,
            total_score=0.68,
            rank=2,
            reason="高分观察",
            risk_note=None,
        ),
    ]

    with patch("app.main.generate_weekly_rebalance", return_value=mock_recommendations):
        client = TestClient(app)
        response = client.post(
            "/api/jobs/run-weekly-strategy",
            params={
                "index_code": "000906",
                "score_date": "2026-05-10",
                "database_url": database_url,
                "limit": 2,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "success"
    assert body["data"]["recommendations_count"] == 2
    assert body["data"]["action_counts"] == {"buy": 1, "hold": 0, "sell": 0, "watch": 1}
    assert "log_id" in body["data"]
    assert "meta" in body

    with open_sqlite_connection(database_url) as connection:
        logs = get_recent_run_logs(connection, task_type="weekly_strategy")

    assert len(logs) == 1
    assert logs[0].status == RunStatus.SUCCESS
    assert logs[0].result["recommendations_count"] == 2


def test_run_weekly_strategy_endpoint_marks_failed_log(tmp_path) -> None:
    """测试手动运行本周策略失败时会记录失败日志。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    with patch("app.main.generate_weekly_rebalance", side_effect=ValueError("bad data")):
        client = TestClient(app)
        response = client.post(
            "/api/jobs/run-weekly-strategy",
            params={
                "index_code": "000906",
                "score_date": "2026-05-10",
                "database_url": database_url,
            },
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "bad data"

    with open_sqlite_connection(database_url) as connection:
        logs = get_recent_run_logs(connection, task_type="weekly_strategy")

    assert len(logs) == 1
    assert logs[0].status == RunStatus.FAILED
    assert logs[0].error_message == "bad data"
