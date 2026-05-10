from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.portfolio import RebalanceRecommendation


@dataclass
class SignalExecution:
    """信号执行记录。"""

    id: int | None = None
    signal_id: int | None = None
    stock_code: str = ""
    action: str = ""
    target_weight: float | None = None
    quantity: int = 0
    price: Decimal = Decimal("0")
    executed_at: str = ""
    status: str = ""
    reason: str = ""


@dataclass
class Signal:
    """策略信号记录。"""

    id: int | None = None
    run_date: str = ""
    stock_code: str = ""
    action: str = ""
    target_weight: float | None = None
    score: float = 0.0
    rank: int | None = None
    reason: str = ""
    risk_note: str | None = None
    created_at: str = ""
    executed: bool = False


def create_signals(
    connection: sqlite3.Connection,
    recommendations: list[RebalanceRecommendation],
    run_date: str,
) -> list[Signal]:
    """创建策略信号记录。

    Args:
        connection: SQLite 连接
        recommendations: 调仓建议列表
        run_date: 运行日期

    Returns:
        创建的信号列表
    """
    now = datetime.now().isoformat()

    signals = []
    for rec in recommendations:
        cursor = connection.execute(
            """
            insert into strategy_signals (
                run_date, stock_code, action, target_weight,
                score, rank, reason, risk_note, created_at, executed
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_date,
                rec.stock_code,
                rec.action,
                rec.target_weight,
                rec.total_score,
                rec.rank,
                rec.reason,
                rec.risk_note,
                now,
                0,
            ),
        )

        signal = Signal(
            id=cursor.lastrowid,
            run_date=run_date,
            stock_code=rec.stock_code,
            action=rec.action,
            target_weight=rec.target_weight,
            score=rec.total_score,
            rank=rec.rank,
            reason=rec.reason,
            risk_note=rec.risk_note,
            created_at=now,
            executed=False,
        )
        signals.append(signal)

    return signals


def record_execution(
    connection: sqlite3.Connection,
    signal_id: int,
    stock_code: str,
    action: str,
    quantity: int,
    price: float,
    status: str,
    reason: str = "",
) -> SignalExecution:
    """记录信号执行。

    Args:
        connection: SQLite 连接
        signal_id: 信号 ID
        stock_code: 股票代码
        action: 买卖方向
        quantity: 数量
        price: 价格
        status: 执行状态
        reason: 原因

    Returns:
        创建的执行记录
    """
    now = datetime.now().isoformat()

    cursor = connection.execute(
        """
        insert into signal_executions (
            signal_id, stock_code, action, quantity,
            price, executed_at, status, reason
        )
        values (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            signal_id,
            stock_code,
            action,
            quantity,
            price,
            now,
            status,
            reason,
        ),
    )

    execution = SignalExecution(
        id=cursor.lastrowid,
        signal_id=signal_id,
        stock_code=stock_code,
        action=action,
        quantity=quantity,
        price=Decimal(str(price)),
        executed_at=now,
        status=status,
        reason=reason,
    )

    # 更新信号状态
    connection.execute(
        """
        update strategy_signals
        set executed = ?
        where id = ?
        """,
        (1 if status == "filled" else 0, signal_id),
    )

    return execution


def get_pending_signals(
    connection: sqlite3.Connection,
    limit: int = 100,
) -> list[Signal]:
    """获取待执行信号。

    Args:
        connection: SQLite 连接
        limit: 返回数量限制

    Returns:
        待执行信号列表
    """
    rows = connection.execute(
        """
        select * from strategy_signals
        where executed = 0
        order by created_at desc
        limit ?
        """,
        (limit,),
    ).fetchall()

    return [
        Signal(
            id=row["id"],
            run_date=row["run_date"],
            stock_code=row["stock_code"],
            action=row["action"],
            target_weight=row["target_weight"],
            score=row["score"],
            rank=row["rank"],
            reason=row["reason"],
            risk_note=row["risk_note"],
            created_at=row["created_at"],
            executed=bool(row["executed"]),
        )
        for row in rows
    ]


def get_execution_summary(
    connection: sqlite3.Connection,
    run_date: str | None = None,
) -> dict[str, Any]:
    """获取执行摘要。

    Args:
        connection: SQLite 连接
        run_date: 运行日期，None 表示全部

    Returns:
        执行摘要
    """
    date_filter = ""

    if run_date:
        date_filter = "where run_date = ?"

    total_signals = connection.execute(
        f"select count(*) from strategy_signals {date_filter}",
        (run_date,) if run_date else (),
    ).fetchone()[0]

    if run_date:
        executed_signals = connection.execute(
            """
            select count(*) from strategy_signals s
            join signal_executions e on s.id = e.signal_id
            where e.status = 'filled'
            and s.run_date = ?
            """,
            (run_date,),
        ).fetchone()[0]
        failed_signals = connection.execute(
            """
            select count(*) from strategy_signals s
            join signal_executions e on s.id = e.signal_id
            where e.status = 'failed'
            and s.run_date = ?
            """,
            (run_date,),
        ).fetchone()[0]
    else:
        executed_signals = connection.execute(
            """
            select count(*) from strategy_signals s
            join signal_executions e on s.id = e.signal_id
            where e.status = 'filled'
            """,
        ).fetchone()[0]
        failed_signals = connection.execute(
            """
            select count(*) from strategy_signals s
            join signal_executions e on s.id = e.signal_id
            where e.status = 'failed'
            """,
        ).fetchone()[0]

    return {
        "total_signals": total_signals,
        "executed_signals": executed_signals,
        "failed_signals": failed_signals,
        "pending_signals": total_signals - executed_signals - failed_signals,
        "execution_rate": executed_signals / total_signals if total_signals > 0 else 0,
    }
