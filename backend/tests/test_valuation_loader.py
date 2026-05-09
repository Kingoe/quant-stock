import pytest

from app.data import (
    ValuationRecord,
    get_valuation_by_trade_date,
    get_valuations,
    load_valuations,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_load_valuations_inserts_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_valuations(
            connection,
            [
                ValuationRecord(
                    stock_code="600000",
                    trade_date="2026-05-08",
                    pe=15.5,
                    pb=1.8,
                    ps=2.5,
                    dividend_yield=0.03,
                )
            ],
        )

        rows = get_valuations(connection, "600000", "2026-05-01", "2026-05-10")

    assert len(rows) == 1
    assert rows[0]["stock_code"] == "600000"
    assert rows[0]["trade_date"] == "2026-05-08"
    assert rows[0]["pe"] == 15.5
    assert rows[0]["pb"] == 1.8
    assert rows[0]["ps"] == 2.5
    assert rows[0]["dividend_yield"] == 0.03


def test_load_valuations_updates_existing_record(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_valuations(
            connection,
            [
                ValuationRecord(
                    stock_code="600000",
                    trade_date="2026-05-08",
                    pe=15.5,
                    pb=1.8,
                    ps=2.5,
                    dividend_yield=0.03,
                )
            ],
        )
        load_valuations(
            connection,
            [
                ValuationRecord(
                    stock_code="600000",
                    trade_date="2026-05-08",
                    pe=16.5,
                    pb=2.0,
                    ps=2.8,
                    dividend_yield=0.035,
                )
            ],
        )

        rows = get_valuations(connection, "600000", "2026-05-08", "2026-05-08")

    assert rows[0]["pe"] == 16.5
    assert rows[0]["pb"] == 2.0
    assert rows[0]["ps"] == 2.8
    assert rows[0]["dividend_yield"] == 0.035


def test_get_valuations_returns_range_ordered_by_trade_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-09", 12.0, 1.5, 2.0, 0.025),
                ValuationRecord("600000", "2026-05-08", 11.5, 1.4, 1.9, 0.024),
                ValuationRecord("000001", "2026-05-08", 20.0, 2.5, 3.0, 0.02),
            ],
        )

        rows = get_valuations(connection, "600000", "2026-05-08", "2026-05-09")

    assert [row["trade_date"] for row in rows] == ["2026-05-08", "2026-05-09"]


def test_get_valuation_by_trade_date_returns_all_for_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-08", 15.5, 1.8, 2.5, 0.03),
                ValuationRecord("000001", "2026-05-08", 20.0, 2.5, 3.0, 0.02),
                ValuationRecord("300750", "2026-05-09", 25.0, 3.0, 3.5, 0.01),
            ],
        )

        rows = get_valuation_by_trade_date(connection, "2026-05-08")

    assert [row["stock_code"] for row in rows] == ["000001", "600000"]


def test_load_valuations_accepts_partial_null_fields(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_valuations(
            connection,
            [
                ValuationRecord(
                    stock_code="600000",
                    trade_date="2026-05-08",
                    pe=15.5,
                    pb=None,
                    ps=None,
                    dividend_yield=None,
                )
            ],
        )

        rows = get_valuations(connection, "600000", "2026-05-08", "2026-05-08")

    assert rows[0]["pe"] == 15.5
    assert rows[0]["pb"] is None
    assert rows[0]["ps"] is None
    assert rows[0]["dividend_yield"] is None


def test_load_valuations_rejects_empty_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="records must not be empty"):
            load_valuations(connection, [])


def test_load_valuations_accepts_all_null_values(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_valuations(
            connection,
            [
                ValuationRecord(
                    stock_code="600000",
                    trade_date="2026-05-08",
                    pe=None,
                    pb=None,
                    ps=None,
                    dividend_yield=None,
                )
            ],
        )

        rows = get_valuations(connection, "600000", "2026-05-08", "2026-05-08")

    assert len(rows) == 1
    assert rows[0]["pe"] is None
    assert rows[0]["pb"] is None
    assert rows[0]["ps"] is None
    assert rows[0]["dividend_yield"] is None
