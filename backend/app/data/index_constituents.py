from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class IndexConstituentRecord:
    index_code: str
    stock_code: str
    trade_date: str
    weight: float | None


def load_index_constituents(
    connection: sqlite3.Connection,
    records: list[IndexConstituentRecord],
) -> None:
    if not records:
        raise ValueError("records must not be empty")

    for record in records:
        connection.execute(
            """
            insert into index_constituents (
                index_code, stock_code, trade_date, weight
            ) values (?, ?, ?, ?)
            on conflict(index_code, stock_code, trade_date) do update set
                weight = excluded.weight
            """,
            (
                record.index_code,
                record.stock_code,
                record.trade_date,
                record.weight,
            ),
        )


def get_index_constituents(
    connection: sqlite3.Connection,
    index_code: str,
    trade_date: str,
) -> list[str]:
    rows = connection.execute(
        """
        select stock_code
        from index_constituents
        where index_code = ?
          and trade_date = ?
        order by stock_code
        """,
        (index_code, trade_date),
    ).fetchall()
    return [row["stock_code"] for row in rows]


def get_latest_index_constituents(
    connection: sqlite3.Connection,
    index_code: str,
    target_date: str,
) -> list[str]:
    row = connection.execute(
        """
        select max(trade_date) as trade_date
        from index_constituents
        where index_code = ?
          and trade_date <= ?
        """,
        (index_code, target_date),
    ).fetchone()
    if row is None or row["trade_date"] is None:
        return []
    return get_index_constituents(connection, index_code, row["trade_date"])
