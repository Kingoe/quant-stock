from __future__ import annotations

import csv
from pathlib import Path


def test_data_update_endpoint_loads_stock_basics_and_logs_success(tmp_path) -> None:
    """测试手动数据更新入口能更新股票基础信息并记录成功日志。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    csv_root = tmp_path / "csv"
    csv_root.mkdir()
    _write_csv(
        csv_root / "stocks.csv",
        ["stock_code", "stock_name", "exchange", "list_date", "industry", "is_st", "status"],
        [
            ["000001", "平安银行", "SZSE", "1991-04-03", "银行", "false", "active"],
            ["600000", "浦发银行", "SSE", "1999-11-10", "银行", "false", "active"],
        ],
    )

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.post(
        "/api/data/update",
        json={
            "database_url": database_url,
            "source": "local_csv",
            "csv_root_dir": str(csv_root),
            "data_type": "stock_basics",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "success"
    assert body["data"]["data_type"] == "stock_basics"
    assert body["data"]["records_count"] == 2
    assert body["data"]["skipped_count"] == 0
    assert "log_id" in body["data"]
    assert "meta" in body

    with open_sqlite_connection(database_url) as connection:
        stock_count = connection.execute("select count(*) as count from stocks").fetchone()
        logs = get_recent_run_logs(connection, task_type="data_update")

    assert stock_count["count"] == 2
    assert len(logs) == 1
    assert logs[0].status == RunStatus.SUCCESS
    assert logs[0].result["data_type"] == "stock_basics"
    assert logs[0].result["records_count"] == 2


def test_data_update_endpoint_loads_daily_prices_for_requested_stocks(tmp_path) -> None:
    """测试手动数据更新入口能按股票和日期范围更新日行情。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    csv_root = tmp_path / "csv"
    csv_root.mkdir()
    _write_csv(
        csv_root / "daily_prices.csv",
        [
            "stock_code",
            "trade_date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "amount",
            "adjusted_close",
            "is_suspended",
            "is_limit_up",
            "is_limit_down",
        ],
        [
            [
                "000001",
                "2026-05-06",
                "10",
                "11",
                "9",
                "10.5",
                "1000",
                "10500",
                "10.5",
                "0",
                "0",
                "0",
            ],
            [
                "000001",
                "2026-05-07",
                "10.5",
                "11.5",
                "10",
                "11",
                "1200",
                "13200",
                "11",
                "0",
                "0",
                "0",
            ],
            [
                "600000",
                "2026-05-07",
                "8",
                "8.2",
                "7.9",
                "8.1",
                "2000",
                "16200",
                "8.1",
                "0",
                "0",
                "0",
            ],
        ],
    )

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.post(
        "/api/data/update",
        json={
            "database_url": database_url,
            "source": "local_csv",
            "csv_root_dir": str(csv_root),
            "data_type": "daily_prices",
            "stock_codes": ["000001"],
            "start_date": "2026-05-06",
            "end_date": "2026-05-07",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "success"
    assert body["data"]["records_count"] == 2
    assert body["data"]["parameters"]["stock_codes"] == ["000001"]

    with open_sqlite_connection(database_url) as connection:
        price_count = connection.execute("select count(*) as count from daily_prices").fetchone()
        logs = get_recent_run_logs(connection, task_type="data_update")

    assert price_count["count"] == 2
    assert logs[0].status == RunStatus.SUCCESS
    assert logs[0].result["records_count"] == 2


def test_data_update_endpoint_supports_remaining_data_types(tmp_path) -> None:
    """测试手动数据更新入口覆盖交易日历、指数成分、估值和财务数据。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    csv_root = tmp_path / "csv"
    csv_root.mkdir()
    _write_csv(
        csv_root / "trading_calendar.csv",
        ["trade_date", "is_open"],
        [["2026-05-06", "1"], ["2026-05-07", "1"]],
    )
    _write_csv(
        csv_root / "index_constituents.csv",
        ["index_code", "stock_code", "trade_date", "weight"],
        [["000906", "000001", "2026-05-07", "0.12"]],
    )
    _write_csv(
        csv_root / "valuations.csv",
        ["stock_code", "trade_date", "pe", "pb", "ps", "dividend_yield"],
        [["000001", "2026-05-07", "10", "1.2", "2.5", "0.03"]],
    )
    _write_csv(
        csv_root / "financial_metrics.csv",
        [
            "stock_code",
            "report_date",
            "disclosure_date",
            "roe",
            "gross_margin",
            "revenue_growth",
            "net_profit_growth",
            "operating_cash_flow",
            "net_profit",
        ],
        [["000001", "2026-03-31", "2026-04-28", "0.12", "0.45", "0.08", "0.1", "1000", "800"]],
    )

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    requests = [
        {
            "data_type": "trading_calendar",
            "start_date": "2026-05-06",
            "end_date": "2026-05-07",
        },
        {
            "data_type": "index_constituents",
            "index_code": "000906",
            "trade_date": "2026-05-07",
        },
        {
            "data_type": "valuation_metrics",
            "trade_date": "2026-05-07",
        },
        {
            "data_type": "financial_metrics",
            "stock_codes": ["000001"],
            "start_date": "2026-03-31",
            "end_date": "2026-03-31",
        },
    ]

    for payload in requests:
        response = client.post(
            "/api/data/update",
            json={
                "database_url": database_url,
                "source": "local_csv",
                "csv_root_dir": str(csv_root),
                **payload,
            },
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "success"

    with open_sqlite_connection(database_url) as connection:
        calendar_count = connection.execute(
            "select count(*) as count from trading_calendar"
        ).fetchone()
        constituent_count = connection.execute(
            "select count(*) as count from index_constituents"
        ).fetchone()
        valuation_count = connection.execute(
            "select count(*) as count from valuation_metrics"
        ).fetchone()
        financial_count = connection.execute(
            "select count(*) as count from financial_metrics"
        ).fetchone()
        logs = get_recent_run_logs(connection, task_type="data_update", limit=10)

    assert calendar_count["count"] == 2
    assert constituent_count["count"] == 1
    assert valuation_count["count"] == 1
    assert financial_count["count"] == 1
    assert len(logs) == 4
    assert all(log.status == RunStatus.SUCCESS for log in logs)


def test_data_update_endpoint_returns_success_for_empty_result(tmp_path) -> None:
    """测试数据源返回空结果时不会把 loader 的空列表限制暴露成失败。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    csv_root = tmp_path / "csv"
    csv_root.mkdir()
    _write_csv(
        csv_root / "valuations.csv",
        ["stock_code", "trade_date", "pe", "pb", "ps", "dividend_yield"],
        [["000001", "2026-05-06", "10", "1.2", "2.5", "0.03"]],
    )

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.post(
        "/api/data/update",
        json={
            "database_url": database_url,
            "source": "local_csv",
            "csv_root_dir": str(csv_root),
            "data_type": "valuation_metrics",
            "trade_date": "2026-05-07",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["records_count"] == 0

    with open_sqlite_connection(database_url) as connection:
        logs = get_recent_run_logs(connection, task_type="data_update")

    assert logs[0].status == RunStatus.SUCCESS
    assert logs[0].result["records_count"] == 0


def test_data_update_endpoint_marks_failed_log_for_unsupported_data_type(tmp_path) -> None:
    """测试不支持的数据类型会返回失败并记录失败日志。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, get_recent_run_logs
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    csv_root = tmp_path / "csv"
    csv_root.mkdir()

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.post(
        "/api/data/update",
        json={
            "database_url": database_url,
            "source": "local_csv",
            "csv_root_dir": str(csv_root),
            "data_type": "not_supported",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert "unsupported data_type" in body["error"]["message"]
    assert "meta" in body

    with open_sqlite_connection(database_url) as connection:
        logs = get_recent_run_logs(connection, task_type="data_update")

    assert len(logs) == 1
    assert logs[0].status == RunStatus.FAILED
    assert "unsupported data_type" in logs[0].error_message


def test_data_update_endpoint_returns_structured_error_for_missing_required_body() -> None:
    """测试请求体缺必填字段时返回统一错误结构。"""
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/data/update",
        json={
            "source": "local_csv",
            "data_type": "stock_basics",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert "请求参数不合法" in body["error"]["message"]
    assert "meta" in body


def test_data_update_endpoint_returns_structured_error_for_bad_database_url() -> None:
    """测试数据库 URL 非法时返回统一错误结构。"""
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.post(
        "/api/data/update",
        json={
            "database_url": "bad-url",
            "source": "local_csv",
            "csv_root_dir": "/tmp",
            "data_type": "stock_basics",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert "database_url" in body["error"]["message"]
    assert "meta" in body


def _write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)
