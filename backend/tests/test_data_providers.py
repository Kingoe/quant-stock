from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest


def test_local_csv_provider_loads_stock_basics(tmp_path) -> None:
    """测试本地 CSV 数据源加载股票基础信息。"""
    from app.data.providers import LocalCsvProvider

    (tmp_path / "stocks.csv").write_text(
        "stock_code,stock_name,exchange,list_date,industry,is_st,status\n"
        "000001,平安银行,SZ,1991-04-03,银行,false,active\n"
        "600000,浦发银行,SH,1999-11-10,银行,0,active\n",
        encoding="utf-8",
    )

    records = LocalCsvProvider(tmp_path).get_stock_basics()

    assert len(records) == 2
    assert records[0].stock_code == "000001"
    assert records[0].stock_name == "平安银行"
    assert records[0].is_st is False


def test_local_csv_provider_rejects_missing_required_columns(tmp_path) -> None:
    """测试本地 CSV 数据源缺少必需字段时显式报错。"""
    from app.data.providers import DataProviderError, LocalCsvProvider

    (tmp_path / "daily_prices.csv").write_text(
        "stock_code,trade_date,close_price\n000001,2026-05-10,10.5\n",
        encoding="utf-8",
    )

    with pytest.raises(DataProviderError, match="missing required columns"):
        LocalCsvProvider(tmp_path).get_daily_prices("000001", "2026-05-01", "2026-05-10")


def test_local_csv_provider_filters_daily_prices_by_stock_and_date(tmp_path) -> None:
    """测试本地 CSV 数据源按股票和日期过滤日行情。"""
    from app.data.providers import LocalCsvProvider

    (tmp_path / "daily_prices.csv").write_text(
        "stock_code,trade_date,open_price,high_price,low_price,close_price,volume,amount,"
        "adjusted_close,is_suspended,is_limit_up,is_limit_down\n"
        "000001,2026-05-08,10,11,9,10.5,1000,10500,10.5,false,false,false\n"
        "000001,2026-05-11,11,12,10,11.5,1000,11500,11.5,false,false,false\n"
        "600000,2026-05-08,8,9,7,8.5,1000,8500,8.5,false,false,false\n",
        encoding="utf-8",
    )

    records = LocalCsvProvider(tmp_path).get_daily_prices("000001", "2026-05-01", "2026-05-10")

    assert len(records) == 1
    assert records[0].stock_code == "000001"
    assert records[0].trade_date == "2026-05-08"
    assert records[0].close_price == 10.5


def test_akshare_provider_converts_stock_basics(monkeypatch) -> None:
    """测试 AkShare 数据源转换股票基础信息。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    fake_akshare = SimpleNamespace(
        stock_info_a_code_name=lambda: pd.DataFrame(
            [
                {"code": "000001", "name": "平安银行"},
                {"code": "600000", "name": "浦发银行"},
            ]
        )
    )
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_stock_basics()

    assert len(records) == 2
    assert records[0].stock_code == "000001"
    assert records[0].exchange == "SZ"
    assert records[1].exchange == "SH"


def test_akshare_provider_converts_daily_prices(monkeypatch) -> None:
    """测试 AkShare 数据源转换日行情。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    calls = {}

    def stock_zh_a_hist(**kwargs):
        calls.update(kwargs)
        return pd.DataFrame(
            [
                {
                    "日期": "2026-05-08",
                    "开盘": 10.0,
                    "最高": 11.0,
                    "最低": 9.0,
                    "收盘": 10.5,
                    "成交量": 1000,
                    "成交额": 10500,
                }
            ]
        )

    fake_akshare = SimpleNamespace(stock_zh_a_hist=stock_zh_a_hist)
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_daily_prices("000001", "2026-05-01", "2026-05-10")

    assert calls["symbol"] == "000001"
    assert calls["start_date"] == "20260501"
    assert calls["end_date"] == "20260510"
    assert len(records) == 1
    assert records[0].trade_date == "2026-05-08"
    assert records[0].adjusted_close == 10.5


def test_akshare_provider_converts_trading_calendar(monkeypatch) -> None:
    """测试 AkShare 数据源转换交易日历。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    fake_akshare = SimpleNamespace(
        tool_trade_date_hist_sina=lambda: pd.DataFrame(
            [
                {"trade_date": "2026-05-08"},
                {"trade_date": "2026-05-11"},
                {"trade_date": "2026-05-12"},
            ]
        )
    )
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_trading_calendar("2026-05-09", "2026-05-12")

    assert [record.trade_date for record in records] == ["2026-05-11", "2026-05-12"]
    assert all(record.is_open for record in records)


def test_akshare_provider_converts_index_constituents(monkeypatch) -> None:
    """测试 AkShare 数据源转换指数成分。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    calls = {}

    def index_stock_cons(symbol):
        calls["symbol"] = symbol
        return pd.DataFrame(
            [
                {"品种代码": "000001", "纳入日期": "2026-05-01", "权重": 0.5},
                {"品种代码": "600000", "纳入日期": "2026-05-01", "权重": 0.3},
            ]
        )

    fake_akshare = SimpleNamespace(index_stock_cons=index_stock_cons)
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_index_constituents("000906", "2026-05-11")

    assert calls["symbol"] == "000906"
    assert len(records) == 2
    assert records[0].index_code == "000906"
    assert [(record.stock_code, record.trade_date, record.weight) for record in records] == [
        ("000001", "2026-05-11", 0.5),
        ("600000", "2026-05-11", 0.3),
    ]


def test_akshare_provider_converts_valuations(monkeypatch) -> None:
    """测试 AkShare 数据源转换估值数据。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    calls = []

    def stock_a_indicator_lg(symbol):
        calls.append(symbol)
        data = {
            "000001": [
                {
                    "trade_date": "2026-05-11",
                    "pe": 5.1,
                    "pb": 0.8,
                    "ps": 2.1,
                    "dv_ratio": 3.2,
                }
            ],
            "600000": [
                {
                    "trade_date": "2026-05-10",
                    "pe": 6.2,
                    "pb": 0.9,
                    "ps": 2.3,
                    "dv_ratio": 2.8,
                }
            ],
        }
        return pd.DataFrame(data[symbol])

    fake_akshare = SimpleNamespace(
        stock_a_indicator_lg=stock_a_indicator_lg,
    )
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider(valuation_symbols=["000001", "600000"]).get_valuations("2026-05-11")

    assert calls == ["000001", "600000"]
    assert len(records) == 1
    assert records[0].stock_code == "000001"
    assert records[0].trade_date == "2026-05-11"
    assert records[0].pe == 5.1
    assert records[0].pb == 0.8
    assert records[0].ps == 2.1
    assert records[0].dividend_yield == 3.2


def test_akshare_provider_reports_missing_required_columns(monkeypatch) -> None:
    """测试 AkShare 字段缺失时返回清晰错误。"""
    import pandas as pd

    from app.data.providers import AkShareProvider, DataProviderError

    fake_akshare = SimpleNamespace(
        stock_a_indicator_lg=lambda symbol="all": pd.DataFrame([{"未知字段": "000001"}])
    )
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    with pytest.raises(DataProviderError, match="missing required AkShare columns"):
        AkShareProvider(valuation_symbols=["000001"]).get_valuations("2026-05-11")


def test_akshare_provider_converts_financial_metrics(monkeypatch) -> None:
    """测试 AkShare 数据源转换财务指标。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    calls = {}

    def stock_financial_abstract(symbol):
        calls["symbol"] = symbol
        return pd.DataFrame(
            [
                {"指标": "净资产收益率", "20260331": "0.12", "20251231": "0.10"},
                {"指标": "销售毛利率", "20260331": "0.31", "20251231": "0.29"},
                {"指标": "营业收入同比增长率", "20260331": "0.18", "20251231": "0.12"},
                {"指标": "净利润同比增长率", "20260331": "0.16", "20251231": "0.11"},
                {
                    "指标": "经营活动产生的现金流量净额",
                    "20260331": "1,200,000.00元",
                    "20251231": "1,000,000.00元",
                },
                {"指标": "净利润", "20260331": "900,000.00元", "20251231": "800,000.00元"},
            ]
        )

    fake_akshare = SimpleNamespace(stock_financial_abstract=stock_financial_abstract)
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_financial_metrics("000001", "2026-01-01", "2026-12-31")

    assert calls["symbol"] == "000001"
    assert len(records) == 1
    assert records[0].stock_code == "000001"
    assert records[0].report_date == "2026-03-31"
    assert records[0].disclosure_date == "2026-03-31"
    assert records[0].roe == 0.12
    assert records[0].gross_margin == 0.31
    assert records[0].revenue_growth == 0.18
    assert records[0].net_profit_growth == 0.16
    assert records[0].operating_cash_flow == 1200000
    assert records[0].net_profit == 900000
