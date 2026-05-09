from __future__ import annotations

import sqlite3


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


def _subtract_months(date_str: str, months: int) -> str:
    """从给定日期减去指定月数，返回格式化的日期字符串"""
    import datetime

    date = datetime.date.fromisoformat(date_str)
    year = date.year - (date.month + months - 1) // 12
    month = ((date.month - months - 1) % 12) + 1
    day = min(date.day, _days_in_month(year, month))
    return datetime.date(year, month, day).isoformat()


def _days_in_month(year: int, month: int) -> int:
    """返回指定年份和月份的天数"""
    import calendar

    return calendar.monthrange(year, month)[1]