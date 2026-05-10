from __future__ import annotations

import sqlite3

SNAPSHOTS_TABLE = "portfolio_snapshots"

SCHEMA_STATEMENTS = [
    """
    create table if not exists stocks (
        stock_code text primary key,
        stock_name text not null,
        exchange text not null,
        list_date text not null,
        industry text,
        is_st integer not null default 0,
        status text not null,
        updated_at text not null default current_timestamp
    )
    """,
    """
    create table if not exists trading_calendar (
        trade_date text primary key,
        is_open integer not null,
        previous_trade_date text,
        next_trade_date text
    )
    """,
    """
    create table if not exists index_constituents (
        index_code text not null,
        stock_code text not null,
        trade_date text not null,
        weight real,
        primary key (index_code, stock_code, trade_date)
    )
    """,
    """
    create table if not exists daily_prices (
        stock_code text not null,
        trade_date text not null,
        open_price real not null,
        high_price real not null,
        low_price real not null,
        close_price real not null,
        volume real not null,
        amount real not null,
        adjusted_close real,
        is_suspended integer not null default 0,
        is_limit_up integer not null default 0,
        is_limit_down integer not null default 0,
        primary key (stock_code, trade_date)
    )
    """,
    """
    create table if not exists valuation_metrics (
        stock_code text not null,
        trade_date text not null,
        pe real,
        pb real,
        ps real,
        dividend_yield real,
        primary key (stock_code, trade_date)
    )
    """,
    """
    create table if not exists financial_metrics (
        stock_code text not null,
        report_date text not null,
        disclosure_date text not null,
        roe real,
        gross_margin real,
        revenue_growth real,
        net_profit_growth real,
        operating_cash_flow real,
        net_profit real,
        primary key (stock_code, report_date)
    )
    """,
    """
    create table if not exists strategy_runs (
        run_id integer primary key autoincrement,
        run_type text not null,
        score_date text not null,
        rebalance_date text,
        status text not null,
        created_at text not null default current_timestamp,
        completed_at text,
        message text
    )
    """,
    """
    create table if not exists rebalance_recommendations (
        recommendation_id integer primary key autoincrement,
        run_id integer not null,
        stock_code text not null,
        stock_name text,
        action text not null,
        target_weight real,
        total_score real,
        reason text,
        risk_note text,
        created_at text not null default current_timestamp,
        foreign key (run_id) references strategy_runs (run_id)
    )
    """,
    f"""
    create table if not exists {SNAPSHOTS_TABLE} (
        snapshot_id integer primary key autoincrement,
        run_id integer not null,
        run_date text not null,
        cash real not null,
        total_value real not null,
        created_at text not null default current_timestamp,
        foreign key (run_id) references strategy_runs (run_id)
    )
    """,
    """
    create index if not exists idx_index_constituents_trade_date
    on index_constituents (trade_date)
    """,
    """
    create index if not exists idx_daily_prices_trade_date
    on daily_prices (trade_date)
    """,
    """
    create index if not exists idx_valuation_metrics_trade_date
    on valuation_metrics (trade_date)
    """,
    """
    create index if not exists idx_financial_metrics_report_date
    on financial_metrics (report_date)
    """,
    """
    create index if not exists idx_rebalance_recommendations_run_id
    on rebalance_recommendations (run_id)
    """,
    f"""
    create index if not exists idx_portfolio_snapshots_run_id
    on {SNAPSHOTS_TABLE} (run_id)
    """,
]


def initialize_schema(connection: sqlite3.Connection) -> None:
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
