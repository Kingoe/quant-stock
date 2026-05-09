from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class DailyPriceRecord:
    stock_code: str
    trade_date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    amount: float
    adjusted_close: float | None = None
    is_suspended: bool = False
    is_limit_up: bool = False
    is_limit_down: bool = False


def load_daily_prices(connection: sqlite3.Connection, records: list[DailyPriceRecord]) -> None:
    if not records:
        raise ValueError("records must not be empty")

    for record in records:
        connection.execute(
            """
            insert into daily_prices (
                stock_code, trade_date, open_price, high_price, low_price, close_price,
                volume, amount, adjusted_close, is_suspended, is_limit_up, is_limit_down
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            on conflict(stock_code, trade_date) do update set
                open_price = excluded.open_price,
                high_price = excluded.high_price,
                low_price = excluded.low_price,
                close_price = excluded.close_price,
                volume = excluded.volume,
                amount = excluded.amount,
                adjusted_close = excluded.adjusted_close,
                is_suspended = excluded.is_suspended,
                is_limit_up = excluded.is_limit_up,
                is_limit_down = excluded.is_limit_down
            """,
            (
                record.stock_code,
                record.trade_date,
                record.open_price,
                record.high_price,
                record.low_price,
                record.close_price,
                record.volume,
                record.amount,
                record.adjusted_close,
                1 if record.is_suspended else 0,
                1 if record.is_limit_up else 0,
                1 if record.is_limit_down else 0,
            ),
        )


def get_daily_prices(
    connection: sqlite3.Connection,
    stock_code: str,
    start_date: str,
    end_date: str,
) -> list[sqlite3.Row]:
    return connection.execute(
        """
        select *
        from daily_prices
        where stock_code = ?
          and trade_date >= ?
          and trade_date <= ?
        order by trade_date
        """,
        (stock_code, start_date, end_date),
    ).fetchall()


def get_prices_by_trade_date(connection: sqlite3.Connection, trade_date: str) -> list[sqlite3.Row]:
    return connection.execute(
        """
        select *
        from daily_prices
        where trade_date = ?
        order by stock_code
        """,
        (trade_date,),
    ).fetchall()
