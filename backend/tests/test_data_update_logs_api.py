from __future__ import annotations


def test_data_update_logs_endpoint_returns_recent_update_logs(tmp_path) -> None:
    """测试数据更新日志 API 返回最近的数据更新任务。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, create_run_log, update_run_log_status
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        first = create_run_log(connection, "data_update")
        update_run_log_status(
            connection,
            first.id,
            RunStatus.SUCCESS,
            result={
                "data_type": "stock_basics",
                "source": "local_csv",
                "records_count": 2,
                "skipped_count": 0,
            },
        )
        second = create_run_log(connection, "data_update")
        update_run_log_status(
            connection,
            second.id,
            RunStatus.FAILED,
            error_message="provider unavailable",
            result={
                "data_type": "daily_prices",
                "source": "akshare",
                "records_count": 0,
                "skipped_count": 0,
            },
        )
        weekly = create_run_log(connection, "weekly_strategy")
        update_run_log_status(connection, weekly.id, RunStatus.SUCCESS)

    client = TestClient(app)
    response = client.get(
        "/api/data/update-logs",
        params={"database_url": database_url},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"data", "meta"}
    assert len(body["data"]) == 2
    assert body["data"][0]["id"] == second.id
    assert body["data"][0]["task_type"] == "data_update"
    assert body["data"][0]["status"] == "failed"
    assert body["data"][0]["error_message"] == "provider unavailable"
    assert body["data"][0]["result"]["data_type"] == "daily_prices"
    assert body["data"][1]["id"] == first.id
    assert body["meta"]["request_id"] == "local-dev"


def test_data_update_logs_endpoint_filters_by_status_and_limit(tmp_path) -> None:
    """测试数据更新日志 API 支持状态过滤和数量限制。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, create_run_log, update_run_log_status
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        success_1 = create_run_log(connection, "data_update")
        update_run_log_status(connection, success_1.id, RunStatus.SUCCESS)
        failed = create_run_log(connection, "data_update")
        update_run_log_status(connection, failed.id, RunStatus.FAILED, error_message="bad data")
        success_2 = create_run_log(connection, "data_update")
        update_run_log_status(connection, success_2.id, RunStatus.SUCCESS)

    client = TestClient(app)
    response = client.get(
        "/api/data/update-logs",
        params={"database_url": database_url, "status": "success", "limit": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == success_2.id
    assert body["data"][0]["status"] == "success"


def test_data_update_logs_endpoint_returns_empty_state(tmp_path) -> None:
    """测试没有数据更新日志时返回稳定空列表。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.run_log import RunStatus, create_run_log, update_run_log_status
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        log = create_run_log(connection, "weekly_strategy")
        update_run_log_status(connection, log.id, RunStatus.SUCCESS)

    client = TestClient(app)
    response = client.get(
        "/api/data/update-logs",
        params={"database_url": database_url},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"] == []
    assert "meta" in body


def test_data_update_logs_endpoint_validates_status(tmp_path) -> None:
    """测试非法状态返回结构化错误。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get(
        "/api/data/update-logs",
        params={"database_url": database_url, "status": "unknown"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert "unsupported status" in body["error"]["message"]
    assert "meta" in body
