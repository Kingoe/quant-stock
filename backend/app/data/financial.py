from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class FinancialRecord:
    stock_code: str
    report_date: str
    disclosure_date: str
    roe: float | None = None
    gross_margin: float | None = None
    revenue_growth: float | None = None
    net_profit_growth: float | None = None
    operating_cash_flow: float | None = None
    net_profit: float | None = None


def load_financial_metrics(connection: sqlite3.Connection, records: list[FinancialRecord]) -> None:
    if not records:
        raise ValueError("records must not be empty")

    for record in records:
        params = (
            record.stock_code,
            record.report_date,
            record.disclosure_date,
            record.roe,
            record.gross_margin,
            record.revenue_growth,
            record.net_profit_growth,
            record.operating_cash_flow,
            record.net_profit,
        )
        connection.execute(
            """
            insert into financial_metrics (
                stock_code, report_date, disclosure_date, roe, gross_margin,
                revenue_growth, net_profit_growth, operating_cash_flow, net_profit
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            on conflict(stock_code, report_date) do update set
                disclosure_date = excluded.disclosure_date,
                roe = excluded.roe,
                gross_margin = excluded.gross_margin,
                revenue_growth = excluded.revenue_growth,
                net_profit_growth = excluded.net_profit_growth,
                operating_cash_flow = excluded.operating_cash_flow,
                net_profit = excluded.net_profit
            """,
            params,
        )


def get_financial_metrics(
    connection: sqlite3.Connection,
    stock_code: str,
    start_date: str,
    end_date: str,
) -> list[sqlite3.Row]:
    return connection.execute(
        """
        select *
        from financial_metrics
        where stock_code = ?
          and report_date >= ?
          and report_date <= ?
        order by report_date
        """,
        (stock_code, start_date, end_date),
    ).fetchall()