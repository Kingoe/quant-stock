from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class StockBasicRecord:
    stock_code: str
    stock_name: str
    exchange: str
    list_date: str
    industry: str | None
    is_st: bool
    status: str


def load_stock_basics(connection: sqlite3.Connection, records: list[StockBasicRecord]) -> None:
    if not records:
        raise ValueError("records must not be empty")

    for record in records:
        connection.execute(
            """
            insert into stocks (
                stock_code, stock_name, exchange, list_date, industry, is_st, status
            ) values (?, ?, ?, ?, ?, ?, ?)
            on conflict(stock_code) do update set
                stock_name = excluded.stock_name,
                exchange = excluded.exchange,
                list_date = excluded.list_date,
                industry = excluded.industry,
                is_st = excluded.is_st,
                status = excluded.status,
                updated_at = current_timestamp
            """,
            (
                record.stock_code,
                record.stock_name,
                record.exchange,
                record.list_date,
                record.industry,
                1 if record.is_st else 0,
                record.status,
            ),
        )


def get_stock(connection: sqlite3.Connection, stock_code: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        select stock_code, stock_name, exchange, list_date, industry, is_st, status
        from stocks
        where stock_code = ?
        """,
        (stock_code,),
    ).fetchone()


def get_active_stock_codes(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        """
        select stock_code
        from stocks
        where status = 'active'
          and is_st = 0
        order by stock_code
        """
    ).fetchall()
    return [row["stock_code"] for row in rows]
