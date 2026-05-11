from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.data.daily_prices import load_daily_prices
from app.data.financial import load_financial_metrics
from app.data.index_constituents import load_index_constituents
from app.data.providers import DataProvider
from app.data.stocks import load_stock_basics
from app.data.trading_calendar import load_trading_calendar
from app.data.valuation import load_valuations


class DataUpdateError(ValueError):
    """数据更新任务错误。"""


class DataUpdateType(StrEnum):
    """支持手动触发的数据类型。"""

    STOCK_BASICS = "stock_basics"
    TRADING_CALENDAR = "trading_calendar"
    INDEX_CONSTITUENTS = "index_constituents"
    DAILY_PRICES = "daily_prices"
    VALUATION_METRICS = "valuation_metrics"
    FINANCIAL_METRICS = "financial_metrics"


@dataclass(frozen=True)
class DataUpdateCommand:
    """数据更新任务参数。"""

    data_type: str
    start_date: str | None = None
    end_date: str | None = None
    trade_date: str | None = None
    index_code: str | None = None
    stock_codes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DataUpdateResult:
    """数据更新任务结果。"""

    data_type: str
    records_count: int
    skipped_count: int
    parameters: dict[str, Any]


def run_data_update(
    connection: sqlite3.Connection,
    provider: DataProvider,
    command: DataUpdateCommand,
) -> DataUpdateResult:
    """执行单次数据更新任务。"""
    try:
        data_type = DataUpdateType(command.data_type)
    except ValueError as exc:
        raise DataUpdateError(f"unsupported data_type: {command.data_type}") from exc

    if data_type == DataUpdateType.STOCK_BASICS:
        records = provider.get_stock_basics()
        if records:
            load_stock_basics(connection, records)
        return _result(command, records_count=len(records))

    if data_type == DataUpdateType.TRADING_CALENDAR:
        start_date = _require(command.start_date, "start_date")
        end_date = _require(command.end_date, "end_date")
        records = provider.get_trading_calendar(start_date, end_date)
        if records:
            load_trading_calendar(connection, records)
        return _result(command, records_count=len(records))

    if data_type == DataUpdateType.INDEX_CONSTITUENTS:
        index_code = _require(command.index_code, "index_code")
        trade_date = _require(command.trade_date, "trade_date")
        records = provider.get_index_constituents(index_code, trade_date)
        if records:
            load_index_constituents(connection, records)
        return _result(command, records_count=len(records))

    if data_type == DataUpdateType.DAILY_PRICES:
        start_date = _require(command.start_date, "start_date")
        end_date = _require(command.end_date, "end_date")
        stock_codes = _require_stock_codes(command.stock_codes)
        all_records = []
        for stock_code in stock_codes:
            all_records.extend(provider.get_daily_prices(stock_code, start_date, end_date))
        if all_records:
            load_daily_prices(connection, all_records)
        return _result(command, records_count=len(all_records), stock_codes=stock_codes)

    if data_type == DataUpdateType.VALUATION_METRICS:
        trade_date = _require(command.trade_date, "trade_date")
        records = provider.get_valuations(trade_date)
        if records:
            load_valuations(connection, records)
        return _result(command, records_count=len(records))

    if data_type == DataUpdateType.FINANCIAL_METRICS:
        start_date = _require(command.start_date, "start_date")
        end_date = _require(command.end_date, "end_date")
        stock_codes = _require_stock_codes(command.stock_codes)
        all_records = []
        for stock_code in stock_codes:
            all_records.extend(provider.get_financial_metrics(stock_code, start_date, end_date))
        if all_records:
            load_financial_metrics(connection, all_records)
        return _result(command, records_count=len(all_records), stock_codes=stock_codes)

    raise DataUpdateError(f"unsupported data_type: {command.data_type}")


def _require(value: str | None, field_name: str) -> str:
    if not value:
        raise DataUpdateError(f"{field_name} is required")
    return value


def _require_stock_codes(stock_codes: list[str]) -> list[str]:
    cleaned = [stock_code.strip() for stock_code in stock_codes if stock_code.strip()]
    if not cleaned:
        raise DataUpdateError("stock_codes is required")
    return cleaned


def _result(
    command: DataUpdateCommand,
    records_count: int,
    stock_codes: list[str] | None = None,
) -> DataUpdateResult:
    parameters: dict[str, Any] = {}
    for key in ("start_date", "end_date", "trade_date", "index_code"):
        value = getattr(command, key)
        if value is not None:
            parameters[key] = value
    if stock_codes is not None:
        parameters["stock_codes"] = stock_codes

    return DataUpdateResult(
        data_type=command.data_type,
        records_count=records_count,
        skipped_count=0,
        parameters=parameters,
    )
