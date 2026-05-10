import sqlite3

import pytest

from app.storage import initialize_schema, open_sqlite_connection

EXPECTED_TABLES = {
    "stocks",
    "trading_calendar",
    "index_constituents",
    "daily_prices",
    "valuation_metrics",
    "financial_metrics",
    "strategy_runs",
    "rebalance_recommendations",
    "parameter_experiments",
    "notification_records",
}


def test_initialize_schema_creates_expected_tables(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        table_names = {
            row["name"]
            for row in connection.execute(
                "select name from sqlite_master where type = 'table'"
            ).fetchall()
        }

    assert EXPECTED_TABLES.issubset(table_names)


def test_initialize_schema_creates_expected_indexes(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        index_names = {
            row["name"]
            for row in connection.execute(
                "select name from sqlite_master where type = 'index'"
            ).fetchall()
        }

    assert {
        "idx_index_constituents_trade_date",
        "idx_daily_prices_trade_date",
        "idx_valuation_metrics_trade_date",
        "idx_financial_metrics_report_date",
        "idx_rebalance_recommendations_run_id",
        "idx_parameter_experiments_created_at",
        "idx_notification_records_created_at",
        "idx_notification_records_channel",
    }.issubset(index_names)


def test_initialize_schema_is_idempotent(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        initialize_schema(connection)

        count = connection.execute("select count(*) as count from stocks").fetchone()

    assert count["count"] == 0


def test_stock_code_primary_key_prevents_duplicates(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            insert into stocks (
                stock_code, stock_name, exchange, list_date, industry, is_st, status
            ) values (?, ?, ?, ?, ?, ?, ?)
            """,
            ("600000", "浦发银行", "SH", "1999-11-10", "银行", 0, "active"),
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                insert into stocks (
                    stock_code, stock_name, exchange, list_date, industry, is_st, status
                ) values (?, ?, ?, ?, ?, ?, ?)
                """,
                ("600000", "浦发银行", "SH", "1999-11-10", "银行", 0, "active"),
            )


def test_daily_prices_unique_stock_code_and_trade_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            insert into daily_prices (
                stock_code, trade_date, open_price, high_price, low_price, close_price,
                volume, amount, adjusted_close
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("600000", "2026-05-08", 10.0, 10.5, 9.8, 10.2, 1000, 10200.0, 10.2),
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                insert into daily_prices (
                    stock_code, trade_date, open_price, high_price, low_price, close_price,
                    volume, amount, adjusted_close
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("600000", "2026-05-08", 10.0, 10.5, 9.8, 10.2, 1000, 10200.0, 10.2),
            )
