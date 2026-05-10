from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class NotificationMessage:
    title: str
    content: str
    level: str = "info"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationSendResult:
    channel: str
    success: bool
    error_message: str | None = None


@dataclass(frozen=True)
class NotificationRecord:
    id: int
    channel: str
    title: str
    content: str
    level: str
    metadata: dict[str, Any]
    status: str
    error_message: str | None
    created_at: str


class NotificationChannel(Protocol):
    channel_name: str

    def send(self, message: NotificationMessage) -> NotificationSendResult: ...


class DatabaseNotificationChannel:
    def __init__(self, connection: sqlite3.Connection, channel_name: str = "local") -> None:
        self.connection = connection
        self.channel_name = channel_name

    def send(self, message: NotificationMessage) -> NotificationSendResult:
        _validate_message(message)
        metadata_json = _dump_json_payload(message.metadata)
        self.connection.execute(
            """
            insert into notification_records (
                channel, title, content, level, metadata, status, error_message
            ) values (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.channel_name,
                message.title.strip(),
                message.content.strip(),
                message.level.strip(),
                metadata_json,
                "success",
                None,
            ),
        )
        return NotificationSendResult(channel=self.channel_name, success=True)


def send_notification(
    message: NotificationMessage,
    channels: Sequence[NotificationChannel],
) -> list[NotificationSendResult]:
    results: list[NotificationSendResult] = []
    for channel in channels:
        try:
            results.append(channel.send(message))
        except Exception as exc:
            results.append(
                NotificationSendResult(
                    channel=channel.channel_name,
                    success=False,
                    error_message=str(exc),
                )
            )
    return results


def list_notifications(
    connection: sqlite3.Connection,
    *,
    limit: int = 20,
    channel: str | None = None,
) -> list[NotificationRecord]:
    if limit <= 0:
        raise ValueError("limit must be greater than 0")

    if channel:
        rows = connection.execute(
            """
            select *
            from notification_records
            where channel = ?
            order by created_at desc, id desc
            limit ?
            """,
            (channel, limit),
        ).fetchall()
    else:
        rows = connection.execute(
            """
            select *
            from notification_records
            order by created_at desc, id desc
            limit ?
            """,
            (limit,),
        ).fetchall()

    return [_row_to_notification_record(row) for row in rows]


def _validate_message(message: NotificationMessage) -> None:
    if not message.title.strip():
        raise ValueError("title must not be empty")
    if not message.content.strip():
        raise ValueError("content must not be empty")
    if not message.level.strip():
        raise ValueError("level must not be empty")
    _dump_json_payload(message.metadata)


def _dump_json_payload(payload: Mapping[str, Any]) -> str:
    try:
        return json.dumps(dict(payload), ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("metadata must be JSON serializable") from exc


def _row_to_notification_record(row: sqlite3.Row) -> NotificationRecord:
    return NotificationRecord(
        id=row["id"],
        channel=row["channel"],
        title=row["title"],
        content=row["content"],
        level=row["level"],
        metadata=json.loads(row["metadata"]),
        status=row["status"],
        error_message=row["error_message"],
        created_at=row["created_at"],
    )
