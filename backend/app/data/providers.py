from __future__ import annotations

import csv
from pathlib import Path
from typing import Protocol

from app.data.daily_prices import DailyPriceRecord
from app.data.financial import FinancialRecord
from app.data.index_constituents import IndexConstituentRecord
from app.data.stocks import StockBasicRecord
from app.data.trading_calendar import TradingCalendarRecord
from app.data.valuation import ValuationRecord


class DataProviderError(ValueError):
    """数据源错误。"""


class DataProvider(Protocol):
    """统一数据源接口。"""

    def get_stock_basics(self) -> list[StockBasicRecord]: ...

    def get_trading_calendar(
        self,
        start_date: str,
        end_date: str,
    ) -> list[TradingCalendarRecord]: ...

    def get_index_constituents(
        self,
        index_code: str,
        trade_date: str,
    ) -> list[IndexConstituentRecord]: ...

    def get_daily_prices(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[DailyPriceRecord]: ...

    def get_valuations(
        self,
        trade_date: str,
    ) -> list[ValuationRecord]: ...

    def get_financial_metrics(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[FinancialRecord]: ...


class LocalCsvProvider:
    """本地 CSV 数据源。"""

    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)

    def get_stock_basics(self) -> list[StockBasicRecord]:
        rows = self._read_rows(
            "stocks.csv",
            {"stock_code", "stock_name", "exchange", "list_date", "industry", "is_st", "status"},
        )
        return [
            StockBasicRecord(
                stock_code=row["stock_code"],
                stock_name=row["stock_name"],
                exchange=row["exchange"],
                list_date=row["list_date"],
                industry=_optional_str(row["industry"]),
                is_st=_to_bool(row["is_st"]),
                status=row["status"],
            )
            for row in rows
        ]

    def get_trading_calendar(self, start_date: str, end_date: str) -> list[TradingCalendarRecord]:
        rows = self._read_rows("trading_calendar.csv", {"trade_date", "is_open"})
        return [
            TradingCalendarRecord(
                trade_date=row["trade_date"],
                is_open=_to_bool(row["is_open"]),
            )
            for row in rows
            if start_date <= row["trade_date"] <= end_date
        ]

    def get_index_constituents(
        self,
        index_code: str,
        trade_date: str,
    ) -> list[IndexConstituentRecord]:
        rows = self._read_rows(
            "index_constituents.csv",
            {"index_code", "stock_code", "trade_date", "weight"},
        )
        return [
            IndexConstituentRecord(
                index_code=row["index_code"],
                stock_code=row["stock_code"],
                trade_date=row["trade_date"],
                weight=_optional_float(row["weight"]),
            )
            for row in rows
            if row["index_code"] == index_code and row["trade_date"] == trade_date
        ]

    def get_daily_prices(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[DailyPriceRecord]:
        rows = self._read_rows(
            "daily_prices.csv",
            {
                "stock_code",
                "trade_date",
                "open_price",
                "high_price",
                "low_price",
                "close_price",
                "volume",
                "amount",
                "adjusted_close",
                "is_suspended",
                "is_limit_up",
                "is_limit_down",
            },
        )
        return [
            _daily_price_from_row(row)
            for row in rows
            if row["stock_code"] == stock_code and start_date <= row["trade_date"] <= end_date
        ]

    def get_valuations(self, trade_date: str) -> list[ValuationRecord]:
        rows = self._read_rows(
            "valuations.csv",
            {"stock_code", "trade_date", "pe", "pb", "ps", "dividend_yield"},
        )
        return [
            ValuationRecord(
                stock_code=row["stock_code"],
                trade_date=row["trade_date"],
                pe=_optional_float(row["pe"]),
                pb=_optional_float(row["pb"]),
                ps=_optional_float(row["ps"]),
                dividend_yield=_optional_float(row["dividend_yield"]),
            )
            for row in rows
            if row["trade_date"] == trade_date
        ]

    def get_financial_metrics(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[FinancialRecord]:
        rows = self._read_rows(
            "financial_metrics.csv",
            {
                "stock_code",
                "report_date",
                "disclosure_date",
                "roe",
                "gross_margin",
                "revenue_growth",
                "net_profit_growth",
                "operating_cash_flow",
                "net_profit",
            },
        )
        return [
            FinancialRecord(
                stock_code=row["stock_code"],
                report_date=row["report_date"],
                disclosure_date=row["disclosure_date"],
                roe=_optional_float(row["roe"]),
                gross_margin=_optional_float(row["gross_margin"]),
                revenue_growth=_optional_float(row["revenue_growth"]),
                net_profit_growth=_optional_float(row["net_profit_growth"]),
                operating_cash_flow=_optional_float(row["operating_cash_flow"]),
                net_profit=_optional_float(row["net_profit"]),
            )
            for row in rows
            if row["stock_code"] == stock_code and start_date <= row["report_date"] <= end_date
        ]

    def _read_rows(self, file_name: str, required_columns: set[str]) -> list[dict[str, str]]:
        path = self.root_dir / file_name
        if not path.exists():
            return []

        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            columns = set(reader.fieldnames or [])
            missing_columns = sorted(required_columns - columns)
            if missing_columns:
                raise DataProviderError(
                    f"{file_name} missing required columns: {', '.join(missing_columns)}"
                )
            return [dict(row) for row in reader]


class AkShareProvider:
    """AkShare 在线数据源适配器。"""

    def __init__(self, adjust: str = "qfq") -> None:
        self.adjust = adjust

    def get_stock_basics(self) -> list[StockBasicRecord]:
        akshare = _import_akshare()
        frame = akshare.stock_info_a_code_name()
        return [
            StockBasicRecord(
                stock_code=str(row["code"]),
                stock_name=str(row["name"]),
                exchange=_infer_exchange(str(row["code"])),
                list_date="1900-01-01",
                industry=None,
                is_st="ST" in str(row["name"]).upper(),
                status="active",
            )
            for _, row in frame.iterrows()
        ]

    def get_daily_prices(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[DailyPriceRecord]:
        akshare = _import_akshare()
        frame = akshare.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", ""),
            adjust=self.adjust,
        )
        return [
            DailyPriceRecord(
                stock_code=stock_code,
                trade_date=str(row["日期"]),
                open_price=float(row["开盘"]),
                high_price=float(row["最高"]),
                low_price=float(row["最低"]),
                close_price=float(row["收盘"]),
                volume=float(row["成交量"]),
                amount=float(row["成交额"]),
                adjusted_close=float(row["收盘"]),
            )
            for _, row in frame.iterrows()
        ]

    def get_trading_calendar(self, start_date: str, end_date: str) -> list[TradingCalendarRecord]:
        raise NotImplementedError("AkShare trading calendar adapter is not implemented yet")

    def get_index_constituents(
        self,
        index_code: str,
        trade_date: str,
    ) -> list[IndexConstituentRecord]:
        raise NotImplementedError("AkShare index constituents adapter is not implemented yet")

    def get_valuations(self, trade_date: str) -> list[ValuationRecord]:
        raise NotImplementedError("AkShare valuation adapter is not implemented yet")

    def get_financial_metrics(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[FinancialRecord]:
        raise NotImplementedError("AkShare financial adapter is not implemented yet")


def _daily_price_from_row(row: dict[str, str]) -> DailyPriceRecord:
    return DailyPriceRecord(
        stock_code=row["stock_code"],
        trade_date=row["trade_date"],
        open_price=float(row["open_price"]),
        high_price=float(row["high_price"]),
        low_price=float(row["low_price"]),
        close_price=float(row["close_price"]),
        volume=float(row["volume"]),
        amount=float(row["amount"]),
        adjusted_close=_optional_float(row["adjusted_close"]),
        is_suspended=_to_bool(row["is_suspended"]),
        is_limit_up=_to_bool(row["is_limit_up"]),
        is_limit_down=_to_bool(row["is_limit_down"]),
    )


def _import_akshare():
    try:
        import akshare
    except ImportError as exc:
        raise DataProviderError("akshare is not installed") from exc
    return akshare


def _infer_exchange(stock_code: str) -> str:
    return "SH" if stock_code.startswith(("5", "6", "9")) else "SZ"


def _optional_str(value: str | None) -> str | None:
    if value is None or value.strip() == "":
        return None
    return value


def _optional_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    return float(value)


def _to_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "是"}
