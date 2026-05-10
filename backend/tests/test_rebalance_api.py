
from app.data import (
    DailyPriceRecord,
    FinancialRecord,
    IndexConstituentRecord,
    StockBasicRecord,
    TradingCalendarRecord,
    ValuationRecord,
    load_daily_prices,
    load_financial_metrics,
    load_index_constituents,
    load_stock_basics,
    load_trading_calendar,
    load_valuations,
)
from app.storage import initialize_schema, open_sqlite_connection
from tests.test_factor_calculators import _build_amount_records


def test_rebalance_api_returns_recommendations(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-01", True),
                TradingCalendarRecord("2026-05-05", True),
                TradingCalendarRecord("2026-05-06", True),
            ],
        )

        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
                StockBasicRecord("300750", "宁德时代", "SZ", "2011-01-01", "新能源", False, "active"),
                StockBasicRecord("601318", "中国平安", "SH", "2007-01-01", "保险", False, "active"),
            ],
        )

        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-05", 0.1),
                IndexConstituentRecord("000906", "000001", "2026-05-05", 0.1),
                IndexConstituentRecord("000906", "600519", "2026-05-05", 0.1),
                IndexConstituentRecord("000906", "300750", "2026-05-05", 0.1),
                IndexConstituentRecord("000906", "601318", "2026-05-05", 0.1),
            ],
        )

        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-05", 5.0, 0.8, None, 0.05),
                ValuationRecord("000001", "2026-05-05", 20.0, 2.0, None, 0.01),
                ValuationRecord("600519", "2026-05-05", 30.0, 5.0, None, 0.01),
                ValuationRecord("300750", "2026-05-05", 40.0, 3.0, None, 0.01),
                ValuationRecord("601318", "2026-05-05", 10.0, 1.5, None, 0.02),
            ],
        )

        load_financial_metrics(
            connection,
            [
                FinancialRecord("600000", "2026-03-31", "2026-04-25", 20.0, 40.0, 20.0, 20.0, 2000.0, 1000.0),
                FinancialRecord("000001", "2026-03-31", "2026-04-25", 5.0, 20.0, 5.0, 5.0, 300.0, 300.0),
                FinancialRecord("600519", "2026-03-31", "2026-04-25", 4.0, 15.0, 3.0, 3.0, 200.0, 300.0),
                FinancialRecord("300750", "2026-03-31", "2026-04-25", 3.0, 10.0, 2.0, 2.0, 100.0, 200.0),
                FinancialRecord("601318", "2026-03-31", "2026-04-25", 6.0, 18.0, 4.0, 4.0, 500.0, 400.0),
            ],
        )

        load_daily_prices(
            connection,
            _build_amount_records(
                {
                    "600000": 30_000_000.0,
                    "000001": 10_000_000.0,
                    "600519": 5_000_000.0,
                    "300750": 20_000_000.0,
                    "601318": 15_000_000.0,
                },
                "2026-05-05",
            )
            + [
                DailyPriceRecord("600000", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("300750", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("601318", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-01-20", 0, 0, 0, 9.0, 100, 900, 9.0),
                DailyPriceRecord("000001", "2026-01-20", 0, 0, 0, 11.0, 100, 1100, 11.0),
                DailyPriceRecord("600519", "2026-01-20", 0, 0, 0, 12.0, 100, 1200, 12.0),
                DailyPriceRecord("300750", "2026-01-20", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("601318", "2026-01-20", 0, 0, 0, 9.0, 100, 900, 9.0),
            ],
        )

    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get(
        "/api/rebalance/latest",
        params={
            "index_code": "000906",
            "score_date": "2026-05-05",
            "database_url": database_url,
            "limit": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert len(data["data"]) == 3

    assert data["data"][0]["action"] == "buy"
    assert "stock_code" in data["data"][0]
    assert "stock_name" in data["data"][0]
    assert "target_weight" in data["data"][0]
    assert "total_score" in data["data"][0]
    assert "rank" in data["data"][0]
    assert "reason" in data["data"][0]
    assert "risk_note" in data["data"][0]


def test_rebalance_api_returns_api_convention_response(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-01", True),
                TradingCalendarRecord("2026-05-05", True),
            ],
        )

        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )

        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("000906", "600000", "2026-05-05", 0.5),
                IndexConstituentRecord("000906", "000001", "2026-05-05", 0.5),
            ],
        )

        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-05", 5.0, 0.8, None, 0.05),
                ValuationRecord("000001", "2026-05-05", 20.0, 2.0, None, 0.01),
            ],
        )

        load_financial_metrics(
            connection,
            [
                FinancialRecord("600000", "2026-03-31", "2026-04-25", 20.0, 40.0, 20.0, 20.0, 2000.0, 1000.0),
                FinancialRecord("000001", "2026-03-31", "2026-04-25", 5.0, 20.0, 5.0, 5.0, 300.0, 300.0),
            ],
        )

        load_daily_prices(
            connection,
            _build_amount_records({"600000": 30_000_000.0, "000001": 10_000_000.0}, "2026-05-05")
            + [
                DailyPriceRecord("600000", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-01-20", 0, 0, 0, 9.0, 100, 900, 9.0),
                DailyPriceRecord("000001", "2026-01-20", 0, 0, 0, 11.0, 100, 1100, 11.0),
            ],
        )

    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get(
        "/api/rebalance/latest",
        params={
            "index_code": "000906",
            "score_date": "2026-05-05",
            "database_url": database_url,
            "limit": 2,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert "request_id" in data["meta"]
    assert "generated_at" in data["meta"]


def test_rebalance_api_returns_empty_for_missing_index(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-01", True),
                TradingCalendarRecord("2026-05-05", True),
            ],
        )

    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get(
        "/api/rebalance/latest",
        params={
            "index_code": "000906",
            "score_date": "2026-05-05",
            "database_url": database_url,
            "limit": 2,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert "meta" in data


def test_rebalance_api_validates_limit_range(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)

    response = client.get(
        "/api/rebalance/latest",
        params={
            "index_code": "000906",
            "score_date": "2026-05-05",
            "database_url": database_url,
            "limit": 0,
        },
    )

    assert response.status_code == 422

    response = client.get(
        "/api/rebalance/latest",
        params={
            "index_code": "000906",
            "score_date": "2026-05-05",
            "database_url": database_url,
            "limit": 100,
        },
    )

    assert response.status_code == 422