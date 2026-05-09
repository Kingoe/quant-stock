from app.data import (
    DailyPriceRecord,
    IndexConstituentRecord,
    StockBasicRecord,
    filter_stocks,
    filter_stocks_by_listing_date,
    filter_stocks_by_suspension,
    get_universe_stock_codes,
    load_daily_prices,
    load_index_constituents,
    load_stock_basics,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_get_universe_stock_codes_returns_active_stocks_from_index(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-01", 0.3),
                IndexConstituentRecord("000906", "600519", "2026-05-01", 0.2),
            ],
        )

        result = get_universe_stock_codes(connection, "000906", "2026-05-07")

    assert set(result) == {"600000", "000001", "600519"}


def test_filter_stocks_removes_st_and_star_st(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "ST平安", "SZ", "2000-01-01", "银行", True, "active"),
                StockBasicRecord("600519", "*ST茅台", "SH", "2001-08-27", "白酒", True, "active"),
                StockBasicRecord("000002", "万科A", "SZ", "2000-01-01", "房地产", False, "active"),
            ],
        )

        result = filter_stocks(connection, ["600000", "000001", "600519", "000002"])

    assert set(result) == {"600000", "000002"}


def test_filter_stocks_keeps_all_non_st_stocks(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )

        result = filter_stocks(connection, ["600000", "000001", "600519"])

    assert set(result) == {"600000", "000001", "600519"}


def test_filter_stocks_returns_empty_when_all_are_st(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("000001", "ST平安", "SZ", "2000-01-01", "银行", True, "active"),
                StockBasicRecord("600519", "*ST茅台", "SH", "2001-08-27", "白酒", True, "active"),
            ],
        )

        result = filter_stocks(connection, ["000001", "600519"])

    assert result == []


def test_filter_stocks_filters_by_is_st_field(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "ST平安", "SZ", "2000-01-01", "银行", True, "active"),
            ],
        )

        result = filter_stocks(connection, ["600000", "000001"])

    assert result == ["600000"]


def test_filter_stocks_only_filters_by_is_st_field(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "ST平安", "SZ", "2000-01-01", "银行", True, "inactive"),
            ],
        )

        result = filter_stocks(connection, ["600000", "000001"])

    assert result == ["600000"]


def test_filter_stocks_by_listing_date_removes_newly_listed(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("600527", "招商银行", "SH", "2025-10-01", "银行", False, "active"),
            ],
        )

        result = filter_stocks_by_listing_date(
            connection, ["600000", "000001", "600519", "600527"], "2026-05-07"
        )

    assert set(result) == {"600000", "000001", "600519"}


def test_filter_stocks_by_listing_date_removes_exactly_one_year_old(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("600527", "招商银行", "SH", "2025-05-07", "银行", False, "active"),
            ],
        )

        result = filter_stocks_by_listing_date(
            connection, ["600000", "000001", "600519", "600527"], "2026-05-07"
        )

    assert set(result) == {"600000", "000001", "600519"}


def test_filter_stocks_by_listing_date_keeps_over_one_year_old(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("600527", "招商银行", "SH", "2025-04-07", "银行", False, "active"),
            ],
        )

        result = filter_stocks_by_listing_date(
            connection, ["600000", "000001", "600519", "600527"], "2026-05-07"
        )

    assert set(result) == {"600000", "000001", "600519", "600527"}


def test_filter_stocks_by_listing_date_supports_custom_months(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("600527", "招商银行", "SH", "2025-10-01", "银行", False, "active"),
            ],
        )

        result = filter_stocks_by_listing_date(
            connection, ["600000", "000001", "600519", "600527"], "2026-05-07", months=18
        )

    assert set(result) == {"600000", "000001", "600519", "600527"}


def test_filter_stocks_by_listing_date_handles_missing_list_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )

        result = filter_stocks_by_listing_date(
            connection, ["600000", "000001", "600519"], "2026-05-07"
        )

    assert set(result) == {"600000", "000001", "600519"}


def test_get_universe_stock_codes_filters_out_st_stocks(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "ST平安", "SZ", "2000-01-01", "银行", True, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-01", 0.3),
                IndexConstituentRecord("000906", "600519", "2026-05-01", 0.2),
            ],
        )

        result = get_universe_stock_codes(connection, "000906", "2026-05-07")

    assert set(result) == {"600000", "600519"}


def test_get_universe_stock_codes_filters_out_inactive_stocks(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord(
                    "000001", "平安银行", "SZ", "2000-01-01", "银行", False, "inactive"
                ),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-01", 0.3),
                IndexConstituentRecord("000906", "600519", "2026-05-01", 0.2),
            ],
        )

        result = get_universe_stock_codes(connection, "000906", "2026-05-07")

    assert set(result) == {"600000", "600519"}


def test_get_universe_stock_codes_uses_latest_available_index_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-01", 0.3),
                IndexConstituentRecord("000906", "600519", "2026-05-15", 0.2),
            ],
        )

        result = get_universe_stock_codes(connection, "000906", "2026-05-10")

    assert set(result) == {"600000", "000001"}


def test_get_universe_stock_codes_filters_out_stocks_not_in_index(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-01", 0.5),
            ],
        )

        result = get_universe_stock_codes(connection, "000906", "2026-05-07")

    assert set(result) == {"600000", "000001"}


def test_get_universe_stock_codes_returns_empty_list_for_missing_index(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
            ],
        )

        result = get_universe_stock_codes(connection, "000906", "2026-05-07")

    assert result == []


def test_filter_stocks_by_suspension_removes_suspended_stocks(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("000002", "万科A", "SZ", "2000-01-01", "房地产", False, "active"),
            ],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    "600000",
                    "2026-05-07",
                    10.0,
                    11.0,
                    9.5,
                    10.5,
                    1000000,
                    10500000.0,
                    None,
                    False,
                    False,
                    False,
                ),
                DailyPriceRecord(
                    "000001", "2026-05-07", 10.0, 10.0, 10.0, 10.0, 0, 0.0, None, True, False, False
                ),
                DailyPriceRecord(
                    "600519",
                    "2026-05-07",
                    1800.0,
                    1850.0,
                    1780.0,
                    1830.0,
                    50000,
                    91500000.0,
                    None,
                    True,
                    False,
                    False,
                ),
                DailyPriceRecord(
                    "000002",
                    "2026-05-07",
                    8.0,
                    8.5,
                    7.8,
                    8.2,
                    2000000,
                    16400000.0,
                    None,
                    False,
                    False,
                    False,
                ),
            ],
        )

        result = filter_stocks_by_suspension(
            connection, ["600000", "000001", "600519", "000002"], "2026-05-07"
        )

    assert set(result) == {"600000", "000002"}


def test_filter_stocks_by_suspension_keeps_all_trading_stocks(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    "600000",
                    "2026-05-07",
                    10.0,
                    11.0,
                    9.5,
                    10.5,
                    1000000,
                    10500000.0,
                    None,
                    False,
                    False,
                    False,
                ),
                DailyPriceRecord(
                    "000001",
                    "2026-05-07",
                    10.0,
                    10.5,
                    9.8,
                    10.3,
                    1200000,
                    12360000.0,
                    None,
                    False,
                    False,
                    False,
                ),
                DailyPriceRecord(
                    "600519",
                    "2026-05-07",
                    1800.0,
                    1850.0,
                    1780.0,
                    1830.0,
                    50000,
                    91500000.0,
                    None,
                    False,
                    False,
                    False,
                ),
            ],
        )

        result = filter_stocks_by_suspension(
            connection, ["600000", "000001", "600519"], "2026-05-07"
        )

    assert set(result) == {"600000", "000001", "600519"}


def test_filter_stocks_by_suspension_returns_empty_when_all_suspended(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    "600000", "2026-05-07", 10.0, 10.0, 10.0, 10.0, 0, 0.0, None, True, False, False
                ),
                DailyPriceRecord(
                    "000001", "2026-05-07", 10.0, 10.0, 10.0, 10.0, 0, 0.0, None, True, False, False
                ),
            ],
        )

        result = filter_stocks_by_suspension(connection, ["600000", "000001"], "2026-05-07")

    assert result == []


def test_filter_stocks_by_suspension_filters_by_is_suspended_field(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    "600000",
                    "2026-05-07",
                    10.0,
                    11.0,
                    9.5,
                    10.5,
                    1000000,
                    10500000.0,
                    None,
                    False,
                    False,
                    False,
                ),
                DailyPriceRecord(
                    "000001", "2026-05-07", 10.0, 10.0, 10.0, 10.0, 0, 0.0, None, True, False, False
                ),
            ],
        )

        result = filter_stocks_by_suspension(connection, ["600000", "000001"], "2026-05-07")

    assert result == ["600000"]


def test_filter_stocks_by_suspension_judges_by_target_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )
        load_daily_prices(
            connection,
            [
                DailyPriceRecord(
                    "600000", "2026-05-06", 10.0, 10.0, 10.0, 10.0, 0, 0.0, None, True, False, False
                ),
                DailyPriceRecord(
                    "600000",
                    "2026-05-07",
                    10.0,
                    11.0,
                    9.5,
                    10.5,
                    1000000,
                    10500000.0,
                    None,
                    False,
                    False,
                    False,
                ),
                DailyPriceRecord(
                    "000001",
                    "2026-05-06",
                    10.0,
                    10.5,
                    9.8,
                    10.3,
                    1200000,
                    12360000.0,
                    None,
                    False,
                    False,
                    False,
                ),
                DailyPriceRecord(
                    "000001", "2026-05-07", 10.0, 10.0, 10.0, 10.0, 0, 0.0, None, True, False, False
                ),
            ],
        )

        result_before = filter_stocks_by_suspension(connection, ["600000", "000001"], "2026-05-06")
        result_after = filter_stocks_by_suspension(connection, ["600000", "000001"], "2026-05-07")

    assert result_before == ["000001"]
    assert result_after == ["600000"]
