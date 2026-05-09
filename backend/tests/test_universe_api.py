from datetime import datetime

from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.data import (
    DailyPriceRecord,
    IndexConstituentRecord,
    StockBasicRecord,
    ValuationRecord,
    load_daily_prices,
    load_index_constituents,
    load_stock_basics,
    load_valuations,
)
from app.main import app
from app.storage import initialize_schema, open_sqlite_connection


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class Meta(BaseModel):
    request_id: str
    generated_at: str
    pagination: PaginationMeta | None = None


class UniverseStockItem(BaseModel):
    stock_code: str
    stock_name: str
    list_date: str
    industry: str
    pe: float | None = None
    pb: float | None = None
    avg_amount: float | None = None
    is_suspended: bool = False


def test_universe_endpoint_returns_filtered_stocks(tmp_path) -> None:
    client = TestClient(app)
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("000002", "万科A", "SZ", "2000-01-01", "房地产", True, "active"),
            ],
        )
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-01", 0.3),
                IndexConstituentRecord("000906", "600519", "2026-05-01", 0.2),
                IndexConstituentRecord("000906", "000002", "2026-05-01", 0.0),
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
                    500000,
                    5000000.0,
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
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None),
                ValuationRecord("000001", "2026-05-07", 4.5, 0.75, None),
                ValuationRecord("600519", "2026-05-07", 30.0, 10.0, None),
                ValuationRecord("000002", "2026-05-07", 8.0, 1.0, None),
            ],
        )

    response = client.get(
        "/api/universe",
        params={"index_code": "000906", "trade_date": "2026-05-07", "database_url": database_url},
    )

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "meta" in body
    assert len(body["data"]) == 3
    stock_codes = {item["stock_code"] for item in body["data"]}
    assert stock_codes == {"600000", "000001", "600519"}


def test_universe_endpoint_applies_all_filters(tmp_path) -> None:
    client = TestClient(app)
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("000002", "万科A", "SZ", "2000-01-01", "房地产", True, "active"),
                StockBasicRecord("600527", "招商银行", "SH", "2025-10-01", "银行", False, "active"),
            ],
        )
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-01", 0.3),
                IndexConstituentRecord("000906", "600519", "2026-05-01", 0.2),
                IndexConstituentRecord("000906", "600527", "2026-05-01", 0.0),
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
                    500000,
                    5000000.0,
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
                DailyPriceRecord(
                    "600527",
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
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None),
                ValuationRecord("000001", "2026-05-07", 4.5, 0.75, None),
                ValuationRecord("600519", "2026-05-07", 30.0, 10.0, None),
                ValuationRecord("000002", "2026-05-07", 8.0, 1.0, None),
                ValuationRecord("600527", "2026-05-07", 7.5, 0.9, None),
            ],
        )

    response = client.get(
        "/api/universe",
        params={
            "index_code": "000906",
            "trade_date": "2026-05-07",
            "database_url": database_url,
            "min_list_months": 12,
            "min_avg_amount": 5000000,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 3
    stock_codes = {item["stock_code"] for item in body["data"]}
    assert stock_codes == {"600000", "000001", "600519"}


def test_universe_endpoint_supports_pagination(tmp_path) -> None:
    client = TestClient(app)
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
                    500000,
                    5000000.0,
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
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None),
                ValuationRecord("000001", "2026-05-07", 4.5, 0.75, None),
                ValuationRecord("600519", "2026-05-07", 30.0, 10.0, None),
            ],
        )

    response = client.get(
        "/api/universe",
        params={
            "index_code": "000906",
            "trade_date": "2026-05-07",
            "database_url": database_url,
            "page": 1,
            "page_size": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 2
    assert body["meta"]["pagination"]["page"] == 1
    assert body["meta"]["pagination"]["page_size"] == 2
    assert body["meta"]["pagination"]["total"] == 3


def test_universe_endpoint_returns_error_on_missing_index(tmp_path) -> None:
    client = TestClient(app)
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )

    response = client.get(
        "/api/universe",
        params={"index_code": "000906", "trade_date": "2026-05-07", "database_url": database_url},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 0


def test_universe_endpoint_returns_api_convention_response(tmp_path) -> None:
    client = TestClient(app)
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_index_constituents(
            connection, [IndexConstituentRecord("000906", "600000", "2026-05-01", 0.5)]
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
                )
            ],
        )
        load_valuations(connection, [ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None)])

    response = client.get(
        "/api/universe",
        params={"index_code": "000906", "trade_date": "2026-05-07", "database_url": database_url},
    )

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "meta" in body
    assert "request_id" in body["meta"]
    assert "generated_at" in body["meta"]
    assert datetime.fromisoformat(body["meta"]["generated_at"])
    assert "pagination" in body["meta"]
