import pytest

from app.notifications import (
    DatabaseNotificationChannel,
    NotificationMessage,
    list_notifications,
    send_notification,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_database_notification_channel_records_successful_message(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        channel = DatabaseNotificationChannel(connection, channel_name="local")

        result = channel.send(
            NotificationMessage(
                title="本周策略已完成",
                content="买入 3 只，卖出 1 只，观察 6 只",
                level="success",
                metadata={"buy": 3, "sell": 1, "watch": 6},
            )
        )
        records = list_notifications(connection)

    assert result.channel == "local"
    assert result.success is True
    assert result.error_message is None
    assert len(records) == 1
    assert records[0].channel == "local"
    assert records[0].title == "本周策略已完成"
    assert records[0].level == "success"
    assert records[0].metadata["buy"] == 3
    assert records[0].status == "success"


def test_send_notification_sends_to_multiple_channels(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        results = send_notification(
            NotificationMessage(title="数据更新完成", content="日行情已更新", level="info"),
            [
                DatabaseNotificationChannel(connection, channel_name="local"),
                DatabaseNotificationChannel(connection, channel_name="audit"),
            ],
        )
        records = list_notifications(connection)

    assert [(result.channel, result.success) for result in results] == [
        ("local", True),
        ("audit", True),
    ]
    assert [record.channel for record in records] == ["audit", "local"]


def test_send_notification_returns_failure_for_failed_channel() -> None:
    class FailedChannel:
        channel_name = "failed"

        def send(self, message: NotificationMessage):
            raise RuntimeError("bad webhook")

    results = send_notification(
        NotificationMessage(title="运行失败", content="策略运行失败", level="error"),
        [FailedChannel()],
    )

    assert len(results) == 1
    assert results[0].channel == "failed"
    assert results[0].success is False
    assert results[0].error_message == "bad webhook"


def test_list_notifications_filters_channel_and_limit(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        local = DatabaseNotificationChannel(connection, channel_name="local")
        audit = DatabaseNotificationChannel(connection, channel_name="audit")
        local.send(NotificationMessage(title="消息 A", content="A"))
        audit.send(NotificationMessage(title="消息 B", content="B"))
        audit.send(NotificationMessage(title="消息 C", content="C"))

        records = list_notifications(connection, channel="audit", limit=1)

    assert len(records) == 1
    assert records[0].channel == "audit"
    assert records[0].title == "消息 C"


def test_notification_message_rejects_invalid_payload(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        channel = DatabaseNotificationChannel(connection)

        with pytest.raises(ValueError, match="title"):
            channel.send(NotificationMessage(title=" ", content="内容"))

        with pytest.raises(ValueError, match="JSON"):
            channel.send(
                NotificationMessage(title="非法元数据", content="内容", metadata={"bad": object()})
            )

        with pytest.raises(ValueError, match="limit"):
            list_notifications(connection, limit=0)
