from __future__ import annotations

import sqlite3
from datetime import datetime
from enum import StrEnum
from typing import Any


class RunStatus(StrEnum):
    """运行状态。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class RunLog:
    """运行日志记录。"""

    def __init__(
        self,
        id: int | None = None,
        task_type: str = "",
        status: RunStatus = RunStatus.PENDING,
        started_at: str | None = None,
        finished_at: str | None = None,
        error_message: str | None = None,
        result: dict[str, Any] | None = None,
    ):
        self.id = id
        self.task_type = task_type
        self.status = status
        self.started_at = started_at
        self.finished_at = finished_at
        self.error_message = error_message
        self.result = result or {}


def create_run_log(
    connection: sqlite3.Connection,
    task_type: str,
) -> RunLog:
    """创建运行日志记录。

    Args:
        connection: SQLite 连接
        task_type: 任务类型

    Returns:
        创建的运行日志
    """
    now = datetime.now().isoformat()

    cursor = connection.execute(
        """
        insert into run_logs (task_type, status, started_at)
        values (?, ?, ?)
        """,
        (task_type, RunStatus.PENDING.value, now),
    )

    return RunLog(
        id=cursor.lastrowid,
        task_type=task_type,
        status=RunStatus.PENDING,
        started_at=now,
    )


def update_run_log_status(
    connection: sqlite3.Connection,
    log_id: int,
    status: RunStatus,
    error_message: str | None = None,
    result: dict[str, Any] | None = None,
) -> None:
    """更新运行日志状态。

    Args:
        connection: SQLite 连接
        log_id: 日志 ID
        status: 新状态
        error_message: 错误信息
        result: 结果数据
    """
    now = datetime.now().isoformat()

    import json

    cursor = connection.execute(
        """
        update run_logs
        set status = ?, finished_at = ?, error_message = ?, result = ?
        where id = ?
        """,
        (
            status.value,
            now,
            error_message,
            json.dumps(result) if result else None,
            log_id,
        ),
    )

    if cursor.rowcount == 0:
        raise ValueError(f"Run log with id {log_id} not found")


def get_recent_run_logs(
    connection: sqlite3.Connection,
    limit: int = 50,
    task_type: str | None = None,
    status: RunStatus | None = None,
) -> list[RunLog]:
    """获取最近的运行日志。

    Args:
        connection: SQLite 连接
        limit: 返回数量限制
        task_type: 筛选任务类型
        status: 筛选运行状态

    Returns:
        运行日志列表
    """
    import json

    query = "select * from run_logs"
    params: list[Any] = []

    where_clauses: list[str] = []

    if task_type:
        where_clauses.append("task_type = ?")
        params.append(task_type)

    if status:
        where_clauses.append("status = ?")
        params.append(status.value)

    if where_clauses:
        query += " where " + " and ".join(where_clauses)

    query += " order by started_at desc limit ?"
    params.append(limit)

    rows = connection.execute(query, params).fetchall()

    return [
        RunLog(
            id=row["id"],
            task_type=row["task_type"],
            status=RunStatus(row["status"]),
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            error_message=row["error_message"],
            result=json.loads(row["result"]) if row["result"] else None,
        )
        for row in rows
    ]
