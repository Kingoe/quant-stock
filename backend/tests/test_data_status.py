from app.data import get_data_status, get_latest_date_by_type
from app.storage import initialize_schema, open_sqlite_connection


def test_get_latest_date_by_type_returns_none_for_empty_table(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        result = get_latest_date_by_type(connection, "daily_prices")

    assert result is None


def test_get_latest_date_by_type_returns_latest_trade_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            insert into daily_prices (stock_code, trade_date, open_price, high_price,
            low_price, close_price, volume, amount)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("600000", "2026-05-06", 10.0, 10.5, 9.8, 10.2, 1000, 10200.0),
        )
        connection.execute(
            """
            insert into daily_prices (stock_code, trade_date, open_price, high_price,
            low_price, close_price, volume, amount)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("600000", "2026-05-07", 11.0, 11.5, 10.8, 11.2, 2000, 22400.0),
        )

        result = get_latest_date_by_type(connection, "daily_prices")

    assert result == "2026-05-07"


def test_get_latest_date_by_type_supports_financial_report_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            insert into financial_metrics (stock_code, report_date, disclosure_date, roe)
            values (?, ?, ?, ?)
            """,
            ("600000", "2026-03-31", "2026-04-28", 12.5),
        )
        connection.execute(
            """
            insert into financial_metrics (stock_code, report_date, disclosure_date, roe)
            values (?, ?, ?, ?)
            """,
            ("600000", "2026-06-30", "2026-07-28", 13.0),
        )

        result = get_latest_date_by_type(connection, "financial_metrics")

    assert result == "2026-06-30"


def test_get_data_status_returns_summary_for_all_data_types(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            insert into daily_prices (stock_code, trade_date, open_price, high_price,
            low_price, close_price, volume, amount)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("600000", "2026-05-07", 10.0, 10.5, 9.8, 10.2, 1000, 10200.0),
        )
        connection.execute(
            """
            insert into valuation_metrics (stock_code, trade_date, pe, pb)
            values (?, ?, ?, ?)
            """,
            ("600000", "2026-05-07", 15.5, 1.8),
        )
        connection.execute(
            """
            insert into financial_metrics (stock_code, report_date, disclosure_date, roe)
            values (?, ?, ?, ?)
            """,
            ("600000", "2026-03-31", "2026-04-28", 12.5),
        )

        result = get_data_status(connection)

    assert result["daily_prices"]["latest_date"] == "2026-05-07"
    assert result["valuation_metrics"]["latest_date"] == "2026-05-07"
    assert result["financial_metrics"]["latest_date"] == "2026-03-31"
    assert result["daily_prices"]["has_data"] is True
    assert result["valuation_metrics"]["has_data"] is True
    assert result["financial_metrics"]["has_data"] is True


def test_get_data_status_handles_missing_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        result = get_data_status(connection)

    assert result["daily_prices"]["latest_date"] is None
    assert result["valuation_metrics"]["latest_date"] is None
    assert result["financial_metrics"]["latest_date"] is None
    assert result["daily_prices"]["has_data"] is False
    assert result["valuation_metrics"]["has_data"] is False
    assert result["financial_metrics"]["has_data"] is False


def test_get_latest_date_by_type_supports_valuation_trade_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            insert into valuation_metrics (stock_code, trade_date, pe, pb)
            values (?, ?, ?, ?)
            """,
            ("600000", "2026-05-06", 15.0, 1.7),
        )
        connection.execute(
            """
            insert into valuation_metrics (stock_code, trade_date, pe, pb)
            values (?, ?, ?, ?)
            """,
            ("600000", "2026-05-07", 15.5, 1.8),
        )

        result = get_latest_date_by_type(connection, "valuation_metrics")

    assert result == "2026-05-07"
