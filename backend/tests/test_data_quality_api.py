from __future__ import annotations


def test_quality_report_endpoint_returns_data_and_meta(tmp_path) -> None:
    """测试数据质量报告 API 返回结构化报告。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get(
        "/api/data/quality-report",
        params={"database_url": database_url, "score_date": "2026-05-12"},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"data", "meta"}
    assert body["data"]["status"] == "error"
    assert body["data"]["score_date"] == "2026-05-12"
    assert body["data"]["summary"]["error"] >= 3
    assert any(issue["code"] == "missing_daily_prices" for issue in body["data"]["issues"])


def test_quality_report_endpoint_returns_structured_error_for_bad_database_url() -> None:
    """测试数据库 URL 非法时返回结构化错误。"""
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get(
        "/api/data/quality-report",
        params={"database_url": "bad-url", "score_date": "2026-05-12"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert "database_url" in body["error"]["message"]
    assert "meta" in body


def test_quality_report_endpoint_returns_structured_error_for_bad_score_date(tmp_path) -> None:
    """测试评分日格式非法时返回结构化错误。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get(
        "/api/data/quality-report",
        params={"database_url": database_url, "score_date": "20260512"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "invalid_request"
    assert body["error"]["details"]["score_date"] == "20260512"
    assert "meta" in body
