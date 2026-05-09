from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class ValuationRecord:
    stock_code: str
    trade_date: str
    pe: float | None = None
    pb: float | None = None
    ps: float | None = None
    dividend_yield: float | None = None


def load_valuations(connection: sqlite3.Connection, records: list[ValuationRecord]) -> None:
    if not records:
        raise ValueError("records must not be empty")

    for record in records:
        params = (
            record.stock_code,
            record.trade_date,
            record.pe,
            record.pb,
            record.ps,
            record.dividend_yield,
        )
        connection.execute(
            """
            insert into valuation_metrics (
                stock_code, trade_date, pe, pb, ps, dividend_yield
            ) values (?, ?, ?, ?, ?, ?)
            on conflict(stock_code, trade_date) do update set
                pe = excluded.pe,
                pb = excluded.pb,
                ps = excluded.ps,
                dividend_yield = excluded.dividend_yield
            """,
            params,
        )


def get_valuations(
    connection: sqlite3.Connection,
    stock_code: str,
    start_date: str,
    end_date: str,
) -> list[sqlite3.Row]:
    return connection.execute(
        """
        select *
        from valuation_metrics
        where stock_code = ?
          and trade_date >= ?
          and trade_date <= ?
        order by trade_date
        """,
        (stock_code, start_date, end_date),
    ).fetchall()


def get_valuation_by_trade_date(
    connection: sqlite3.Connection, trade_date: str
) -> list[sqlite3.Row]:
    return connection.execute(
        """
        select *
        from valuation_metrics
        where trade_date = ?
        order by stock_code
        """,
        (trade_date,),
    ).fetchall()
