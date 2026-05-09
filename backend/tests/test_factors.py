from app.data import (
    DailyPriceRecord,
    FinancialRecord,
    StockBasicRecord,
    ValuationRecord,
    get_aligned_daily_price,
    get_aligned_financial,
    get_aligned_valuation,
    load_daily_prices,
    load_financial_metrics,
    load_stock_basics,
    load_valuations,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_get_aligned_daily_price_returns_latest_before_score_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-05", 10.0, 11.0, 9.5, 10.5, 1000000, 10500000.0, None, False, False, False),
                DailyPriceRecord("600000", "2026-05-06", 10.2, 11.2, 9.7, 10.7, 1100000, 11070000.0, None, False, False, False),
                DailyPriceRecord("600000", "2026-05-07", 10.5, 11.5, 10.0, 11.0, 1200000, 11640000.0, None, False, False, False),
            ],
        )

        result = get_aligned_daily_price(connection, "600000", "2026-05-07")

    assert result is not None
    assert result["trade_date"] == "2026-05-07"
    assert result["close_price"] == 11.0


def test_get_aligned_daily_price_returns_nearest_before_score_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-05", 10.0, 11.0, 9.5, 10.5, 1000000, 10500000.0, None, False, False, False),
                DailyPriceRecord("600000", "2026-05-06", 10.2, 11.2, 9.7, 10.7, 1100000, 11070000.0, None, False, False, False),
            ],
        )

        result = get_aligned_daily_price(connection, "600000", "2026-05-07")

    assert result is not None
    assert result["trade_date"] == "2026-05-06"
    assert result["close_price"] == 10.7


def test_get_aligned_daily_price_returns_none_when_no_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-08", 10.0, 11.0, 9.5, 10.5, 1000000, 10500000.0, None, False, False, False),
            ],
        )

        result = get_aligned_daily_price(connection, "600000", "2026-05-07")

    assert result is None


def test_get_aligned_valuation_returns_latest_before_score_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-05", 5.0, 0.8, None),
                ValuationRecord("600000", "2026-05-06", 5.1, 0.81, None),
                ValuationRecord("600000", "2026-05-07", 5.2, 0.82, None),
            ],
        )

        result = get_aligned_valuation(connection, "600000", "2026-05-07")

    assert result is not None
    assert result["trade_date"] == "2026-05-07"
    assert result["pe"] == 5.2


def test_get_aligned_valuation_returns_nearest_before_score_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-05", 5.0, 0.8, None),
                ValuationRecord("600000", "2026-05-06", 5.1, 0.81, None),
            ],
        )

        result = get_aligned_valuation(connection, "600000", "2026-05-07")

    assert result is not None
    assert result["trade_date"] == "2026-05-06"
    assert result["pe"] == 5.1


def test_get_aligned_financial_returns_latest_disclosed_before_score_date(
    tmp_path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord("600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0),
                FinancialRecord("600000", "2026-06-30", "2026-08-10", 12.0, 32.0, 6.0, 10.0, 1200.0, 600.0),
            ],
        )

        result = get_aligned_financial(connection, "600000", "2026-05-07")

    assert result is not None
    assert result["report_date"] == "2026-03-31"
    assert result["disclosure_date"] == "2026-04-25"
    assert result["roe"] == 10.0


def test_get_aligned_financial_filters_future_report_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord("600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0),
                FinancialRecord("600000", "2026-06-30", "2026-04-20", 12.0, 32.0, 6.0, 10.0, 1200.0, 600.0),
            ],
        )

        result = get_aligned_financial(connection, "600000", "2026-05-07")

    assert result is not None
    assert result["report_date"] == "2026-03-31"
    assert result["disclosure_date"] == "2026-04-25"


def test_get_aligned_financial_filters_future_disclosure_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord("600000", "2026-03-31", "2026-05-10", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0),
                FinancialRecord("600000", "2025-12-31", "2026-04-15", 9.0, 28.0, 4.0, 7.0, 900.0, 450.0),
            ],
        )

        result = get_aligned_financial(connection, "600000", "2026-05-07")

    assert result is not None
    assert result["report_date"] == "2025-12-31"
    assert result["disclosure_date"] == "2026-04-15"


def test_get_aligned_financial_returns_none_when_no_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord("600000", "2026-06-30", "2026-08-10", 12.0, 32.0, 6.0, 10.0, 1200.0, 600.0),
            ],
        )

        result = get_aligned_financial(connection, "600000", "2026-05-07")

    assert result is None
