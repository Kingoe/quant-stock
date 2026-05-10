from __future__ import annotations

from app.backtest.trading_rules import (
    TradingConstraints,
    TradingDayStatus,
    filter_orders_by_trading_constraints,
    get_default_trading_constraints,
)


def test_filter_orders_t_plus_one_blocks_same_day_sell() -> None:
    """测试 T+1 限制阻止当日买入当日卖出。"""
    orders = [
        ("000001", "buy", 1000, 10.0),
        ("000001", "sell", 500, 10.0),
    ]
    trading_day_status = {"000001": TradingDayStatus()}
    buy_stocks_today = {"000001"}
    constraints = TradingConstraints(t_plus_one=True)

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, buy_stocks_today, constraints
    )

    assert len(filtered) == 1
    assert filtered[0][1] == "buy"


def test_filter_orders_t_plus_one_allows_different_day_sell() -> None:
    """测试 T+1 限制允许不同日卖出。"""
    orders = [("000001", "sell", 500, 10.0)]
    trading_day_status = {"000001": TradingDayStatus()}
    buy_stocks_today = set()
    constraints = TradingConstraints(t_plus_one=True)

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, buy_stocks_today, constraints
    )

    assert len(filtered) == 1
    assert filtered[0][1] == "sell"


def test_filter_orders_limit_up_blocks_buy() -> None:
    """测试涨停阻止买入。"""
    orders = [("000001", "buy", 1000, 10.0)]
    trading_day_status = {"000001": TradingDayStatus(is_limit_up=True)}
    constraints = TradingConstraints(limit_up=True)

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, constraints=constraints
    )

    assert len(filtered) == 0


def test_filter_orders_limit_up_allows_sell() -> None:
    """测试涨停允许卖出。"""
    orders = [("000001", "sell", 1000, 10.0)]
    trading_day_status = {"000001": TradingDayStatus(is_limit_up=True)}
    constraints = TradingConstraints(limit_up=True)

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, constraints=constraints
    )

    assert len(filtered) == 1
    assert filtered[0][1] == "sell"


def test_filter_orders_limit_down_blocks_sell() -> None:
    """测试跌停阻止卖出。"""
    orders = [("000001", "sell", 1000, 10.0)]
    trading_day_status = {"000001": TradingDayStatus(is_limit_down=True)}
    constraints = TradingConstraints(limit_down=True)

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, constraints=constraints
    )

    assert len(filtered) == 0


def test_filter_orders_limit_down_allows_buy() -> None:
    """测试跌停允许买入。"""
    orders = [("000001", "buy", 1000, 10.0)]
    trading_day_status = {"000001": TradingDayStatus(is_limit_down=True)}
    constraints = TradingConstraints(limit_down=True)

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, constraints=constraints
    )

    assert len(filtered) == 1
    assert filtered[0][1] == "buy"


def test_filter_orders_suspended_blocks_all() -> None:
    """测试停牌阻止所有交易。"""
    orders = [
        ("000001", "buy", 1000, 10.0),
        ("000001", "sell", 500, 10.0),
    ]
    trading_day_status = {"000001": TradingDayStatus(is_suspended=True)}
    constraints = TradingConstraints(suspended=True)

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, constraints=constraints
    )

    assert len(filtered) == 0


def test_filter_orders_allows_normal_trading() -> None:
    """测试正常交易不受限制。"""
    orders = [
        ("000001", "buy", 1000, 10.0),
        ("000002", "sell", 500, 10.0),
    ]
    trading_day_status = {
        "000001": TradingDayStatus(),
        "000002": TradingDayStatus(),
    }
    constraints = TradingConstraints()

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, constraints=constraints
    )

    assert len(filtered) == 2


def test_filter_orders_with_default_constraints() -> None:
    """测试默认约束配置。"""
    orders = [("000001", "sell", 500, 10.0)]
    trading_day_status = {"000001": TradingDayStatus(is_limit_down=True)}

    filtered = filter_orders_by_trading_constraints(orders, trading_day_status)

    assert len(filtered) == 0  # 默认约束包含跌停限制


def test_get_default_trading_constraints() -> None:
    """测试默认交易约束配置。"""
    constraints = get_default_trading_constraints()

    assert constraints.t_plus_one is True
    assert constraints.limit_up is True
    assert constraints.limit_down is True
    assert constraints.suspended is True


def test_filter_orders_multiple_constraints() -> None:
    """测试多个约束同时生效。"""
    orders = [
        ("000001", "buy", 1000, 10.0),  # 涨停，不允许买入
        ("000002", "sell", 500, 10.0),  # 跌停，不允许卖出
        ("000003", "sell", 200, 10.0),  # T+1，当日买入不允许卖出
    ]
    trading_day_status = {
        "000001": TradingDayStatus(is_limit_up=True),
        "000002": TradingDayStatus(is_limit_down=True),
        "000003": TradingDayStatus(),
    }
    buy_stocks_today = {"000003"}

    filtered = filter_orders_by_trading_constraints(orders, trading_day_status, buy_stocks_today)

    assert len(filtered) == 0


def test_filter_orders_missing_status() -> None:
    """测试缺失交易状态时使用默认状态。"""
    orders = [("000001", "buy", 1000, 10.0)]
    trading_day_status = {}
    constraints = TradingConstraints()

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, constraints=constraints
    )

    assert len(filtered) == 1


def test_filter_orders_disabled_constraints() -> None:
    """测试禁用约束时允许交易。"""
    orders = [
        ("000001", "buy", 1000, 10.0),
        ("000001", "sell", 500, 10.0),
    ]
    trading_day_status = {
        "000001": TradingDayStatus(is_limit_up=True, is_limit_down=True, is_suspended=True)
    }
    constraints = TradingConstraints(
        t_plus_one=False, limit_up=False, limit_down=False, suspended=False
    )

    filtered = filter_orders_by_trading_constraints(
        orders, trading_day_status, buy_stocks_today={"000001"}, constraints=constraints
    )

    assert len(filtered) == 2  # 所有限制禁用，允许所有交易


def test_filter_orders_empty_input() -> None:
    """测试空输入返回空列表。"""
    filtered = filter_orders_by_trading_constraints([], {})
    assert filtered == []
