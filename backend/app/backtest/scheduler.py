from __future__ import annotations

import sqlite3
from datetime import date, timedelta

from app.data import get_open_trade_dates


def generate_weekly_rebalance_dates(
    connection: sqlite3.Connection,
    start_date: str,
    end_date: str,
    rebalance_day: str = "Friday",
) -> list[str]:
    """根据交易日历生成周频调仓日期。

    Args:
        connection: SQLite 连接
        start_date: 起始日期
        end_date: 截止日期
        rebalance_day: 每周调仓日（"Friday" 表示周五）

    Returns:
        调仓日期列表，按日期排序

    调仓日选择规则：
    - 每周选择 rebalance_day 指定的工作日
    - 调仓日必须是开市日
    - 按日期范围生成调仓日列表
    """
    open_dates = get_open_trade_dates(connection, start_date, end_date)

    rebalance_dates = []
    for trade_date in open_dates:
        day_of_week = date.fromisoformat(trade_date).weekday()
        if rebalance_day == "Friday" and day_of_week == 4:
            rebalance_dates.append(trade_date)

    return rebalance_dates


def get_next_trade_date_after(
    connection: sqlite3.Connection,
    target_date: str,
) -> str | None:
    """获取目标日期之后的第一个交易日。

    Args:
        connection: SQLite 连接
        target_date: 目标日期

    Returns:
        目标日期之后的第一个交易日，如果找不到则返回 None
    """
    end_date = (date.fromisoformat(target_date) + timedelta(days=365)).isoformat()
    open_dates = get_open_trade_dates(connection, target_date, end_date)

    for trade_date in open_dates:
        if date.fromisoformat(trade_date) > date.fromisoformat(target_date):
            return trade_date

    return None