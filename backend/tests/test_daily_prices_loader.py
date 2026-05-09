import pytest

from app.data import DailyPriceRecord, get_daily_prices, get_prices_by_trade_date, load_daily_prices
from app.storage import initialize_schema, open_sqlite_connection


def test_load_daily_prices_inserts_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    stock_code="600000",
                    trade_date="2026-05-08",
                    open_price=10.0,
                    high_price=10.5,
                    low_price=9.8,
                    close_price=10.2,
                    volume=1000,
                    amount=10200.0,
                    adjusted_close=10.2,
                    is_suspended=False,
                    is_limit_up=False,
                    is_limit_down=False,
                )
            ],
        )

        rows = get_daily_prices(connection, "600000", "2026-05-01", "2026-05-10")

    assert len(rows) == 1
    assert rows[0]["stock_code"] == "600000"
    assert rows[0]["trade_date"] == "2026-05-08"
    assert rows[0]["open_price"] == 10.0
    assert rows[0]["high_price"] == 10.5
    assert rows[0]["low_price"] == 9.8
    assert rows[0]["close_price"] == 10.2
    assert rows[0]["volume"] == 1000
    assert rows[0]["amount"] == 10200.0
    assert rows[0]["adjusted_close"] == 10.2
    assert rows[0]["is_suspended"] == 0


def test_load_daily_prices_updates_existing_record(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    "600000",
                    "2026-05-08",
                    10.0,
                    10.5,
                    9.8,
                    10.2,
                    1000,
                    10200.0,
                    10.2,
                    False,
                    False,
                    False,
                )
            ],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    "600000",
                    "2026-05-08",
                    11.0,
                    11.5,
                    10.8,
                    11.2,
                    2000,
                    22400.0,
                    11.2,
                    True,
                    True,
                    False,
                )
            ],
        )

        rows = get_daily_prices(connection, "600000", "2026-05-08", "2026-05-08")

    assert rows[0]["open_price"] == 11.0
    assert rows[0]["volume"] == 2000
    assert rows[0]["is_suspended"] == 1
    assert rows[0]["is_limit_up"] == 1
    assert rows[0]["is_limit_down"] == 0


def test_get_daily_prices_returns_range_ordered_by_trade_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-09", 11, 12, 10, 11.5, 100, 1150, 11.5),
                DailyPriceRecord("600000", "2026-05-08", 10, 11, 9, 10.5, 100, 1050, 10.5),
                DailyPriceRecord("000001", "2026-05-08", 20, 21, 19, 20.5, 100, 2050, 20.5),
            ],
        )

        rows = get_daily_prices(connection, "600000", "2026-05-08", "2026-05-09")

    assert [row["trade_date"] for row in rows] == ["2026-05-08", "2026-05-09"]


def test_get_prices_by_trade_date_returns_all_prices_for_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-08", 10, 11, 9, 10.5, 100, 1050, 10.5),
                DailyPriceRecord("000001", "2026-05-08", 20, 21, 19, 20.5, 100, 2050, 20.5),
                DailyPriceRecord("300750", "2026-05-09", 30, 31, 29, 30.5, 100, 3050, 30.5),
            ],
        )

        rows = get_prices_by_trade_date(connection, "2026-05-08")

    assert [row["stock_code"] for row in rows] == ["000001", "600000"]


def test_load_daily_prices_rejects_empty_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="records must not be empty"):
            load_daily_prices(connection, [])
