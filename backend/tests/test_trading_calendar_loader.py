import pytest

from app.data import (
    TradingCalendarRecord,
    get_next_open_trade_date,
    get_open_trade_dates,
    load_trading_calendar,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_load_trading_calendar_inserts_records_and_links_open_days(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-08", True),
                TradingCalendarRecord("2026-05-09", False),
                TradingCalendarRecord("2026-05-11", True),
                TradingCalendarRecord("2026-05-12", True),
            ],
        )

        rows = connection.execute(
            """
            select trade_date, is_open, previous_trade_date, next_trade_date
            from trading_calendar
            order by trade_date
            """
        ).fetchall()

    assert [row["trade_date"] for row in rows] == [
        "2026-05-08",
        "2026-05-09",
        "2026-05-11",
        "2026-05-12",
    ]
    assert rows[0]["previous_trade_date"] is None
    assert rows[0]["next_trade_date"] == "2026-05-11"
    assert rows[1]["is_open"] == 0
    assert rows[1]["previous_trade_date"] == "2026-05-08"
    assert rows[1]["next_trade_date"] == "2026-05-11"
    assert rows[2]["previous_trade_date"] == "2026-05-08"
    assert rows[2]["next_trade_date"] == "2026-05-12"


def test_load_trading_calendar_updates_existing_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-08", True),
                TradingCalendarRecord("2026-05-09", False),
            ],
        )
        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-08", True),
                TradingCalendarRecord("2026-05-09", True),
            ],
        )

        row = connection.execute(
            "select is_open, previous_trade_date from trading_calendar where trade_date = ?",
            ("2026-05-09",),
        ).fetchone()

    assert row["is_open"] == 1
    assert row["previous_trade_date"] == "2026-05-08"


def test_get_open_trade_dates_returns_open_days_in_range(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-08", True),
                TradingCalendarRecord("2026-05-09", False),
                TradingCalendarRecord("2026-05-11", True),
            ],
        )

        trade_dates = get_open_trade_dates(connection, "2026-05-08", "2026-05-11")

    assert trade_dates == ["2026-05-08", "2026-05-11"]


def test_get_next_open_trade_date_returns_first_open_day_after_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-08", True),
                TradingCalendarRecord("2026-05-09", False),
                TradingCalendarRecord("2026-05-11", True),
            ],
        )

        next_trade_date = get_next_open_trade_date(connection, "2026-05-08")

    assert next_trade_date == "2026-05-11"


def test_load_trading_calendar_rejects_empty_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="records must not be empty"):
            load_trading_calendar(connection, [])
