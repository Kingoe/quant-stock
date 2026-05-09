from app.data import (
    IndexConstituentRecord,
    StockBasicRecord,
    filter_st_stocks,
    get_universe_stock_codes,
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


def test_filter_st_stocks_removes_st_and_star_st(tmp_path) -> None:
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

        result = filter_st_stocks(connection, ["600000", "000001", "600519", "000002"])

    assert set(result) == {"600000", "000002"}


def test_filter_st_stocks_keeps_all_non_st_stocks(tmp_path) -> None:
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

        result = filter_st_stocks(connection, ["600000", "000001", "600519"])

    assert set(result) == {"600000", "000001", "600519"}


def test_filter_st_stocks_returns_empty_when_all_are_st(tmp_path) -> None:
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

        result = filter_st_stocks(connection, ["000001", "600519"])

    assert result == []


def test_filter_st_stocks_filters_by_is_st_field(tmp_path) -> None:
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

        result = filter_st_stocks(connection, ["600000", "000001"])

    assert result == ["600000"]


def test_filter_st_stocks_only_filters_by_is_st_field(tmp_path) -> None:
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

        result = filter_st_stocks(connection, ["600000", "000001"])

    assert result == ["600000"]


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