from __future__ import annotations


def test_notifications_endpoint_returns_recent_records(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.notifications import DatabaseNotificationChannel, NotificationMessage
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        channel = DatabaseNotificationChannel(connection, channel_name="local")
        channel.send(
            NotificationMessage(
                title="本周策略已完成",
                content="生成 12 条建议",
                level="success",
                metadata={"recommendations": 12},
            )
        )

    client = TestClient(app)
    response = client.get("/api/notifications", params={"database_url": database_url})

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"data", "meta"}
    assert len(body["data"]) == 1
    assert body["data"][0]["channel"] == "local"
    assert body["data"][0]["title"] == "本周策略已完成"
    assert body["data"][0]["level"] == "success"
    assert body["data"][0]["metadata"]["recommendations"] == 12
    assert body["data"][0]["status"] == "success"
    assert body["meta"]["request_id"] == "local-dev"


def test_notifications_endpoint_filters_by_channel_and_limit(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.notifications import DatabaseNotificationChannel, NotificationMessage
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        local = DatabaseNotificationChannel(connection, channel_name="local")
        audit = DatabaseNotificationChannel(connection, channel_name="audit")
        local.send(NotificationMessage(title="消息 A", content="A"))
        audit.send(NotificationMessage(title="消息 B", content="B"))
        audit.send(NotificationMessage(title="消息 C", content="C"))

    client = TestClient(app)
    response = client.get(
        "/api/notifications",
        params={"database_url": database_url, "channel": "audit", "limit": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["channel"] == "audit"
    assert body["data"][0]["title"] == "消息 C"


def test_notifications_endpoint_returns_empty_state(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get("/api/notifications", params={"database_url": database_url})

    assert response.status_code == 200
    body = response.json()
    assert body["data"] == []
    assert "meta" in body


def test_notifications_endpoint_validates_limit(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get("/api/notifications", params={"database_url": database_url, "limit": 0})

    assert response.status_code == 422
