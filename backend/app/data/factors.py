from __future__ import annotations

import sqlite3


def get_aligned_daily_price(
    connection: sqlite3.Connection, stock_code: str, score_date: str
) -> sqlite3.Row | None:
    """获取评分日或之前最近交易日的日行情"""
    return connection.execute(
        """
        select *
        from daily_prices
        where stock_code = ?
          and trade_date = (
            select max(trade_date)
            from daily_prices
            where stock_code = ?
              and trade_date <= ?
          )
        """,
        (stock_code, stock_code, score_date),
    ).fetchone()


def get_aligned_valuation(
    connection: sqlite3.Connection, stock_code: str, score_date: str
) -> sqlite3.Row | None:
    """获取评分日或之前最近估值日的估值数据"""
    return connection.execute(
        """
        select *
        from valuation_metrics
        where stock_code = ?
          and trade_date = (
            select max(trade_date)
            from valuation_metrics
            where stock_code = ?
              and trade_date <= ?
          )
        """,
        (stock_code, stock_code, score_date),
    ).fetchone()


def get_aligned_financial(
    connection: sqlite3.Connection, stock_code: str, score_date: str
) -> sqlite3.Row | None:
    """获取评分日时已披露的最新财务数据

    财务数据需要同时满足：
    1. 报告期 <= 评分日
    2. 披露日期 <= 评分日
    返回最新的一条（按报告期排序）
    """
    return connection.execute(
        """
        select *
        from financial_metrics
        where stock_code = ?
          and report_date <= ?
          and disclosure_date <= ?
        order by report_date desc
        limit 1
        """,
        (stock_code, score_date, score_date),
    ).fetchone()
