from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta


def get_universe_stock_codes(
    connection: sqlite3.Connection, index_code: str, target_date: str
) -> list[str]:
    from app.data import get_active_stock_codes, get_latest_index_constituents

    latest_codes = get_latest_index_constituents(connection, index_code, target_date)
    active_codes = set(get_active_stock_codes(connection))
    return [code for code in latest_codes if code in active_codes]


def filter_stocks(connection: sqlite3.Connection, stock_codes: list[str]) -> list[str]:
    rows = connection.execute(
        """
        select stock_code
        from stocks
        where stock_code in ({})
          and is_st = 0
        """.format(",".join("?" * len(stock_codes))),
        stock_codes,
    ).fetchall()
    return [row["stock_code"] for row in rows]


def filter_stocks_by_listing_date(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    target_date: str,
    months: int = 12,
) -> list[str]:
    cutoff_date = _subtract_months(target_date, months)
    rows = connection.execute(
        """
        select stock_code
        from stocks
        where stock_code in ({})
          and list_date < ?
        """.format(",".join("?" * len(stock_codes))),
        [*stock_codes, cutoff_date],
    ).fetchall()
    return [row["stock_code"] for row in rows]


def filter_stocks_by_suspension(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    trade_date: str,
) -> list[str]:
    if not stock_codes:
        return []
    placeholders = ",".join("?" * len(stock_codes))
    rows = connection.execute(
        f"""
        select stock_code
        from daily_prices
        where stock_code in ({placeholders})
          and trade_date = ?
          and is_suspended = 0
        """,
        [*stock_codes, trade_date],
    ).fetchall()
    return [row["stock_code"] for row in rows]


def filter_stocks_by_liquidity(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    target_date: str,
    threshold: float = 5000000,
    window: int = 20,
) -> list[str]:
    if not stock_codes:
        return []

    start_date = _subtract_days(target_date, window - 1)
    placeholders = ",".join("?" * len(stock_codes))
    rows = connection.execute(
        f"""
        select stock_code, avg(amount) as avg_amount
        from daily_prices
        where stock_code in ({placeholders})
          and trade_date >= ?
          and trade_date <= ?
        group by stock_code
        having avg_amount >= ?
        """,
        [*stock_codes, start_date, target_date, threshold],
    ).fetchall()
    return [row["stock_code"] for row in rows]


def _subtract_months(date_str: str, months: int) -> str:
    """从给定日期减去指定月数，返回格式化的日期字符串"""
    date = datetime.fromisoformat(date_str).date()
    year = date.year - (date.month + months - 1) // 12
    month = ((date.month - months - 1) % 12) + 1
    day = min(date.day, _days_in_month(year, month))
    return datetime.fromisoformat(f"{year}-{month:02d}-{day:02d}").date().isoformat()


def _subtract_days(date_str: str, days: int) -> str:
    """从给定日期减去指定天数，返回格式化的日期字符串"""
    date = datetime.fromisoformat(date_str).date()
    return (date - timedelta(days=days)).isoformat()


def _days_in_month(year: int, month: int) -> int:
    """返回指定年份和月份的天数"""
    import calendar

    return calendar.monthrange(year, month)[1]
