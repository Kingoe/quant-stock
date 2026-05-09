import pytest

from app.data import (
    FinancialRecord,
    get_financial_metrics,
    load_financial_metrics,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_load_financial_metrics_inserts_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    stock_code="600000",
                    report_date="2026-03-31",
                    disclosure_date="2026-04-28",
                    roe=12.5,
                    gross_margin=35.2,
                    revenue_growth=8.5,
                    net_profit_growth=10.2,
                    operating_cash_flow=5000000.0,
                    net_profit=3000000.0,
                )
            ],
        )

        rows = get_financial_metrics(connection, "600000", "2026-01-01", "2026-03-31")

    assert len(rows) == 1
    assert rows[0]["stock_code"] == "600000"
    assert rows[0]["report_date"] == "2026-03-31"
    assert rows[0]["disclosure_date"] == "2026-04-28"
    assert rows[0]["roe"] == 12.5
    assert rows[0]["gross_margin"] == 35.2
    assert rows[0]["revenue_growth"] == 8.5
    assert rows[0]["net_profit_growth"] == 10.2
    assert rows[0]["operating_cash_flow"] == 5000000.0
    assert rows[0]["net_profit"] == 3000000.0


def test_load_financial_metrics_updates_existing_record(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    stock_code="600000",
                    report_date="2026-03-31",
                    disclosure_date="2026-04-28",
                    roe=12.5,
                    gross_margin=35.2,
                    revenue_growth=8.5,
                    net_profit_growth=10.2,
                    operating_cash_flow=5000000.0,
                    net_profit=3000000.0,
                )
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    stock_code="600000",
                    report_date="2026-03-31",
                    disclosure_date="2026-04-29",
                    roe=13.0,
                    gross_margin=36.0,
                    revenue_growth=9.0,
                    net_profit_growth=11.0,
                    operating_cash_flow=5500000.0,
                    net_profit=3200000.0,
                )
            ],
        )

        rows = get_financial_metrics(connection, "600000", "2026-03-31", "2026-03-31")

    assert rows[0]["roe"] == 13.0
    assert rows[0]["disclosure_date"] == "2026-04-29"
    assert rows[0]["operating_cash_flow"] == 5500000.0


def test_get_financial_metrics_returns_range_ordered_by_report_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000",
                    "2026-03-31",
                    "2026-04-28",
                    12.5,
                    35.2,
                    8.5,
                    10.2,
                    5000000.0,
                    3000000.0,
                ),
                FinancialRecord(
                    "600000",
                    "2025-12-31",
                    "2026-03-28",
                    11.5,
                    34.5,
                    7.5,
                    9.5,
                    4500000.0,
                    2800000.0,
                ),
                FinancialRecord(
                    "000001",
                    "2026-03-31",
                    "2026-04-25",
                    8.0,
                    25.0,
                    5.0,
                    6.0,
                    2000000.0,
                    1500000.0,
                ),
            ],
        )

        rows = get_financial_metrics(connection, "600000", "2025-12-01", "2026-03-31")

    assert [row["report_date"] for row in rows] == ["2025-12-31", "2026-03-31"]


def test_load_financial_metrics_accepts_partial_null_fields(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    stock_code="600000",
                    report_date="2026-03-31",
                    disclosure_date="2026-04-28",
                    roe=12.5,
                    gross_margin=None,
                    revenue_growth=None,
                    net_profit_growth=None,
                    operating_cash_flow=None,
                    net_profit=None,
                )
            ],
        )

        rows = get_financial_metrics(connection, "600000", "2026-03-31", "2026-03-31")

    assert rows[0]["roe"] == 12.5
    assert rows[0]["gross_margin"] is None
    assert rows[0]["revenue_growth"] is None
    assert rows[0]["net_profit_growth"] is None
    assert rows[0]["operating_cash_flow"] is None
    assert rows[0]["net_profit"] is None


def test_load_financial_metrics_rejects_empty_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="records must not be empty"):
            load_financial_metrics(connection, [])


def test_load_financial_metrics_accepts_all_null_values(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    stock_code="600000",
                    report_date="2026-03-31",
                    disclosure_date="2026-04-28",
                    roe=None,
                    gross_margin=None,
                    revenue_growth=None,
                    net_profit_growth=None,
                    operating_cash_flow=None,
                    net_profit=None,
                )
            ],
        )

        rows = get_financial_metrics(connection, "600000", "2026-03-31", "2026-03-31")

    assert len(rows) == 1
    assert rows[0]["roe"] is None
    assert rows[0]["gross_margin"] is None
    assert rows[0]["revenue_growth"] is None
    assert rows[0]["net_profit_growth"] is None
    assert rows[0]["operating_cash_flow"] is None
    assert rows[0]["net_profit"] is None