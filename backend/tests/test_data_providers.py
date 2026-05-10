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
