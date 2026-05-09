from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TradingCalendarRecord:
    trade_date: str
    is_open: bool


def load_trading_calendar(
    connection: sqlite3.Connection,
    records: list[TradingCalendarRecord],
) -> None:
    if not records:
        raise ValueError("records must not be empty")

    sorted_records = sorted(records, key=lambda record: _parse_date(record.trade_date))
    open_dates = [record.trade_date for record in sorted_records if record.is_open]

    for record in sorted_records:
        previous_trade_date = _previous_open_date(open_dates, record.trade_date)
        next_trade_date = _next_open_date(open_dates, record.trade_date)
        connection.execute(
            """
            insert into trading_calendar (
                trade_date, is_open, previous_trade_date, next_trade_date
            ) values (?, ?, ?, ?)
            on conflict(trade_date) do update set
                is_open = excluded.is_open,
                previous_trade_date = excluded.previous_trade_date,
                next_trade_date = excluded.next_trade_date
            """,
            (
                record.trade_date,
                1 if record.is_open else 0,
                previous_trade_date,
                next_trade_date,
            ),
        )


def get_open_trade_dates(
    connection: sqlite3.Connection,
    start_date: str,
    end_date: str,
) -> list[str]:
    rows = connection.execute(
        """
        select trade_date
        from trading_calendar
        where is_open = 1
          and trade_date >= ?
          and trade_date <= ?
        order by trade_date
        """,
        (start_date, end_date),
    ).fetchall()
    return [row["trade_date"] for row in rows]


def get_next_open_trade_date(connection: sqlite3.Connection, trade_date: str) -> str | None:
    row = connection.execute(
        """
        select trade_date
        from trading_calendar
        where is_open = 1
          and trade_date > ?
        order by trade_date
        limit 1
        """,
        (trade_date,),
    ).fetchone()
    if row is None:
        return None
    return row["trade_date"]


def _previous_open_date(open_dates: list[str], trade_date: str) -> str | None:
    previous_dates = [open_date for open_date in open_dates if open_date < trade_date]
    if not previous_dates:
        return None
    return previous_dates[-1]


def _next_open_date(open_dates: list[str], trade_date: str) -> str | None:
    next_dates = [open_date for open_date in open_dates if open_date > trade_date]
    if not next_dates:
        return None
    return next_dates[0]


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)
