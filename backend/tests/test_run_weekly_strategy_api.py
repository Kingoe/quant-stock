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
        _insert_complete_preflight_data(connection, "2026-05-10")

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
    assert body["data"]["preflight"]["status"] == "passed"
    assert "log_id" in body["data"]
    assert "meta" in body

    with open_sqlite_connection(database_url) as connection:
        logs = get_recent_run_logs(connection, task_type="weekly_strategy")

    assert len(logs) == 1
    assert logs[0].status == RunStatus.SUCCESS
    assert logs[0].result["recommendations_count"] == 2
    assert logs[0].result["preflight"]["status"] == "passed"


def test_run_weekly_strategy_endpoint_marks_failed_log(tmp_path) -> None:
    """测试手动运行本周策略失败时会记录失败日志。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        _insert_complete_preflight_data(connection, "2026-05-10")

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
    assert logs[0].result["preflight"]["status"] == "passed"


def test_run_weekly_strategy_endpoint_allows_warning_preflight(tmp_path) -> None:
    """测试前置检查只有 warning 时允许运行并返回风险提示。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.portfolio import RebalanceRecommendation
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        _insert_complete_preflight_data(connection, "2026-05-10")
        connection.execute(
            "update valuation_metrics set trade_date = ? where stock_code = ?",
            ("2026-05-09", "000001"),
        )

    mock_recommendations = [
        RebalanceRecommendation(
            stock_code="000001",
            stock_name="平安银行",
            action="hold",
            target_weight=0.08,
            total_score=0.75,
            rank=1,
            reason="维持持仓",
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
                "limit": 1,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "success"
    assert body["data"]["preflight"]["status"] == "warning"
    assert any(
        issue["code"] == "stale_valuation_metrics"
        for issue in body["data"]["preflight"]["warning_issues"]
    )

    with open_sqlite_connection(database_url) as connection:
        logs = get_recent_run_logs(connection, task_type="weekly_strategy")

    assert len(logs) == 1
    assert logs[0].status == RunStatus.SUCCESS
    assert logs[0].result["preflight"]["status"] == "warning"


def test_run_weekly_strategy_endpoint_blocks_when_preflight_fails(tmp_path) -> None:
    """测试前置检查失败时阻止策略运行并记录失败日志。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    with patch("app.main.generate_weekly_rebalance") as generate_mock:
        client = TestClient(app)
        response = client.post(
            "/api/jobs/run-weekly-strategy",
            params={
                "index_code": "000906",
                "score_date": "2026-05-10",
                "database_url": database_url,
            },
        )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "preflight_failed"
    assert body["error"]["details"]["preflight"]["status"] == "blocked"
    generate_mock.assert_not_called()

    with open_sqlite_connection(database_url) as connection:
        logs = get_recent_run_logs(connection, task_type="weekly_strategy")

    assert len(logs) == 1
    assert logs[0].status == RunStatus.FAILED
    assert logs[0].result["preflight"]["status"] == "blocked"


def _insert_complete_preflight_data(connection, score_date: str) -> None:
    connection.execute(
        """
        insert into stocks (stock_code, stock_name, exchange, list_date, industry, is_st, status)
        values (?, ?, ?, ?, ?, ?, ?)
        """,
        ("000001", "平安银行", "SZSE", "2020-01-01", "银行", 0, "active"),
    )
    connection.execute(
        """
        insert into daily_prices (
            stock_code, trade_date, open_price, high_price, low_price, close_price,
            volume, amount, adjusted_close, is_suspended, is_limit_up, is_limit_down
        )
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("000001", score_date, 10, 11, 9, 10.5, 1000, 1000000, 10.5, 0, 0, 0),
    )
    connection.execute(
        """
        insert into valuation_metrics (stock_code, trade_date, pe, pb, ps, dividend_yield)
        values (?, ?, ?, ?, ?, ?)
        """,
        ("000001", score_date, 12.5, 1.2, 2.0, 0.03),
    )
    connection.execute(
        """
        insert into financial_metrics (
            stock_code, report_date, disclosure_date, roe, gross_margin,
            revenue_growth, net_profit_growth, operating_cash_flow, net_profit
        )
        values (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("000001", "2026-03-31", "2026-04-25", 0.12, 0.45, 0.08, 0.1, 1000, 800),
    )
