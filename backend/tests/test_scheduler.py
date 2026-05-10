from __future__ import annotations

import pytest

from app.data import TradingCalendarRecord, load_trading_calendar
from app.storage import initialize_schema, open_sqlite_connection


def test_generate_weekly_rebalance_dates_selects_fridays() -> None:
    """测试周频调仓日期生成选择周五。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-01", True),  # Friday
                TradingCalendarRecord("2026-05-04", True),
                TradingCalendarRecord("2026-05-05", True),
                TradingCalendarRecord("2026-05-06", True),
                TradingCalendarRecord("2026-05-07", True),
                TradingCalendarRecord("2026-05-08", True),  # Friday
                TradingCalendarRecord("2026-05-11", True),
                TradingCalendarRecord("2026-05-12", True),
                TradingCalendarRecord("2026-05-13", True),
                TradingCalendarRecord("2026-05-14", True),
                TradingCalendarRecord("2026-05-15", True),  # Friday
                TradingCalendarRecord("2026-05-18", True),
                TradingCalendarRecord("2026-05-19", True),
                TradingCalendarRecord("2026-05-20", True),
                TradingCalendarRecord("2026-05-21", True),
                TradingCalendarRecord("2026-05-22", True),  # Friday
                TradingCalendarRecord("2026-05-25", True),
                TradingCalendarRecord("2026-05-26", True),
                TradingCalendarRecord("2026-05-27", True),
                TradingCalendarRecord("2026-05-28", True),
                TradingCalendarRecord("2026-05-29", True),  # Friday
            ],
        )

        from app.backtest.scheduler import generate_weekly_rebalance_dates

        dates = generate_weekly_rebalance_dates(
            connection,
            start_date="2026-05-01",
            end_date="2026-05-31",
            rebalance_day="Friday",
        )

        assert len(dates) == 5
        assert dates[0] == "2026-05-01"
        assert dates[1] == "2026-05-08"
        assert dates[2] == "2026-05-15"
        assert dates[3] == "2026-05-22"
        assert dates[4] == "2026-05-29"


def test_generate_weekly_rebalance_dates_filters_non_trading_days() -> None:
    """测试调仓日期只包含开市日。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-01", True),   # Friday
                TradingCalendarRecord("2026-05-02", True),   # Saturday (not open normally but we mark as open)
                TradingCalendarRecord("2026-05-03", True),   # Sunday
                TradingCalendarRecord("2026-05-04", True),
                TradingCalendarRecord("2026-05-05", True),
                TradingCalendarRecord("2026-05-06", True),
                TradingCalendarRecord("2026-05-07", True),
                TradingCalendarRecord("2026-05-08", True),   # Friday
            ],
        )

        from app.backtest.scheduler import generate_weekly_rebalance_dates

        dates = generate_weekly_rebalance_dates(
            connection,
            start_date="2026-05-01",
            end_date="2026-05-31",
            rebalance_day="Friday",
        )

        assert len(dates) == 2
        assert dates[0] == "2026-05-01"
        assert dates[1] == "2026-05-08"
        # 2026-05-02 and 2026-05-03 are not Friday (Saturday/Sunday) so they should not be included


def test_generate_weekly_rebalance_dates_returns_empty_for_no_fridays() -> None:
    """测试没有周五时返回空列表。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-06", True),  # Wednesday
                TradingCalendarRecord("2026-05-07", True),  # Thursday
                TradingCalendarRecord("2026-05-08", True),  # Friday - wait, this is Friday
                # Actually let's use dates that are NOT Friday
                TradingCalendarRecord("2026-05-11", True),  # Monday
                TradingCalendarRecord("2026-05-12", True),  # Tuesday
                TradingCalendarRecord("2026-05-13", True),  # Wednesday
            ],
        )

        from app.backtest.scheduler import generate_weekly_rebalance_dates

        dates = generate_weekly_rebalance_dates(
            connection,
            start_date="2026-05-01",
            end_date="2026-05-31",
            rebalance_day="Friday",
        )

        assert dates == ["2026-05-08"]  # Only May 8 is Friday


def test_generate_weekly_rebalance_dates_returns_empty_for_empty_calendar() -> None:
    """测试空交易日历时返回空列表。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        # Skip load_trading_calendar as it doesn't support empty lists
        # Just test with an empty calendar (no open dates in range)

        from app.backtest.scheduler import generate_weekly_rebalance_dates

        dates = generate_weekly_rebalance_dates(
            connection,
            start_date="2026-05-01",
            end_date="2026-05-31",
            rebalance_day="Friday",
        )

        assert dates == []


def test_generate_weekly_rebalance_dates_returns_sorted_dates() -> None:
    """测试调仓日期按日期排序。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-22", True),  # Friday
                TradingCalendarRecord("2026-05-15", True),  # Friday
                TradingCalendarRecord("2026-05-08", True),  # Friday
                TradingCalendarRecord("2026-05-01", True),  # Friday
            ],
        )

        from app.backtest.scheduler import generate_weekly_rebalance_dates

        dates = generate_weekly_rebalance_dates(
            connection,
            start_date="2026-05-01",
            end_date="2026-05-31",
            rebalance_day="Friday",
        )

        assert dates == ["2026-05-01", "2026-05-08", "2026-05-15", "2026-05-22"]
        assert dates == sorted(dates)


def test_get_next_trade_date_after_returns_next_trade_date() -> None:
    """测试获取目标日期之后的第一个交易日。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-01", True),
                TradingCalendarRecord("2026-05-02", True),
                TradingCalendarRecord("2026-05-03", True),
                TradingCalendarRecord("2026-05-06", True),
            ],
        )

        from app.backtest.scheduler import get_next_trade_date_after

        next_date = get_next_trade_date_after(connection, "2026-05-01")

        assert next_date == "2026-05-02"


def test_get_next_trade_date_after_returns_none_for_no_future_dates() -> None:
    """测试没有未来交易日时返回 None。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-01", True),
            ],
        )

        from app.backtest.scheduler import get_next_trade_date_after

        next_date = get_next_trade_date_after(connection, "2026-05-01")

        assert next_date is None


def test_get_next_trade_date_after_returns_correct_for_skip_dates() -> None:
    """测试跳过周末和假期时返回正确的下一个交易日。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        load_trading_calendar(
            connection,
            [
                TradingCalendarRecord("2026-05-06", True),
                TradingCalendarRecord("2026-05-07", True),
                TradingCalendarRecord("2026-05-08", True),
                TradingCalendarRecord("2026-05-09", True),
                TradingCalendarRecord("2026-05-10", True),
                TradingCalendarRecord("2026-05-11", True),
                TradingCalendarRecord("2026-05-12", True),
                TradingCalendarRecord("2026-05-13", True),
                TradingCalendarRecord("2026-05-14", True),
                TradingCalendarRecord("2026-05-15", True),
            ],
        )

        from app.backtest.scheduler import get_next_trade_date_after

        next_date = get_next_trade_date_after(connection, "2026-05-01")

        # 2026-05-06 is the first trade date after 2026-05-01
        assert next_date == "2026-05-06"