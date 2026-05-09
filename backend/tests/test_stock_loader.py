import pytest

from app.data import StockBasicRecord, get_active_stock_codes, get_stock, load_stock_basics
from app.storage import initialize_schema, open_sqlite_connection


def test_load_stock_basics_inserts_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord(
                    stock_code="600000",
                    stock_name="浦发银行",
                    exchange="SH",
                    list_date="1999-11-10",
                    industry="银行",
                    is_st=False,
                    status="active",
                ),
                StockBasicRecord(
                    stock_code="000001",
                    stock_name="平安银行",
                    exchange="SZ",
                    list_date="1991-04-03",
                    industry="银行",
                    is_st=False,
                    status="active",
                ),
            ],
        )

        stock = get_stock(connection, "600000")

    assert stock is not None
    assert stock["stock_code"] == "600000"
    assert stock["stock_name"] == "浦发银行"
    assert stock["exchange"] == "SH"
    assert stock["list_date"] == "1999-11-10"
    assert stock["industry"] == "银行"
    assert stock["is_st"] == 0
    assert stock["status"] == "active"


def test_load_stock_basics_updates_existing_record(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord(
                    stock_code="600000",
                    stock_name="浦发银行",
                    exchange="SH",
                    list_date="1999-11-10",
                    industry="银行",
                    is_st=False,
                    status="active",
                )
            ],
        )
        load_stock_basics(
            connection,
            [
                StockBasicRecord(
                    stock_code="600000",
                    stock_name="浦发银行",
                    exchange="SH",
                    list_date="1999-11-10",
                    industry="金融",
                    is_st=True,
                    status="suspended",
                )
            ],
        )

        stock = get_stock(connection, "600000")

    assert stock["industry"] == "金融"
    assert stock["is_st"] == 1
    assert stock["status"] == "suspended"


def test_get_active_stock_codes_returns_only_active_non_st_codes(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "1999-11-10", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "1991-04-03", "银行", True, "active"),
                StockBasicRecord(
                    "300750", "宁德时代", "SZ", "2018-06-11", "电力设备", False, "delisted"
                ),
            ],
        )

        stock_codes = get_active_stock_codes(connection)

    assert stock_codes == ["600000"]


def test_get_stock_returns_none_when_missing(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        stock = get_stock(connection, "999999")

    assert stock is None


def test_load_stock_basics_rejects_empty_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="records must not be empty"):
            load_stock_basics(connection, [])
