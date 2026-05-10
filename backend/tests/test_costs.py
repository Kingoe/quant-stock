from __future__ import annotations

import pytest

from app.backtest.costs import (
    TradingCost,
    TradeResult,
    calculate_trading_cost,
    get_default_trading_cost,
)


def test_calculate_trading_cost_for_buy() -> None:
    """测试买入交易成本计算。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)
    result = calculate_trading_cost("000001", "buy", 1000, 10.0, cost)

    assert result.stock_code == "000001"
    assert result.action == "buy"
    assert result.quantity == 1000
    assert result.price == 10.0
    assert result.execution_price == pytest.approx(10.01)  # 10 * (1 + 0.001)
    assert result.commission == 5.0  # 10010 * 0.0003 = 3.003 < 5
    assert result.stamp_duty == 0.0
    assert result.total_cost == 5.0
    assert result.net_value == pytest.approx(-10015.0)


def test_calculate_trading_cost_for_sell() -> None:
    """测试卖出交易成本计算。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)
    result = calculate_trading_cost("000001", "sell", 1000, 10.0, cost)

    assert result.stock_code == "000001"
    assert result.action == "sell"
    assert result.quantity == 1000
    assert result.price == 10.0
    assert result.execution_price == pytest.approx(9.99)  # 10 * (1 - 0.001)
    assert result.commission == 5.0  # 9990 * 0.0003 = 2.997 < 5
    assert result.stamp_duty == pytest.approx(9.99)  # 9990 * 0.001
    assert result.total_cost == pytest.approx(14.99)
    assert result.net_value == pytest.approx(9975.01)


def test_calculate_trading_cost_commission_min() -> None:
    """测试最低佣金规则。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)
    result = calculate_trading_cost("000001", "buy", 100, 10.0, cost)

    assert result.commission == 5.0  # 10.01 * 100 * 0.0003 = 0.3003 < 5


def test_calculate_trading_cost_slippage() -> None:
    """测试滑点计算。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)

    buy_result = calculate_trading_cost("000001", "buy", 1000, 10.0, cost)
    assert buy_result.execution_price > buy_result.price  # 买入价格上涨

    sell_result = calculate_trading_cost("000001", "sell", 1000, 10.0, cost)
    assert sell_result.execution_price < sell_result.price  # 卖出价格下跌


def test_calculate_trading_cost_stamp_duty_only_on_sell() -> None:
    """测试印花税仅在卖出时收取。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)

    buy_result = calculate_trading_cost("000001", "buy", 1000, 10.0, cost)
    assert buy_result.stamp_duty == 0.0

    sell_result = calculate_trading_cost("000001", "sell", 1000, 10.0, cost)
    assert sell_result.stamp_duty > 0.0


def test_get_default_trading_cost() -> None:
    """测试默认交易成本配置。"""
    cost = get_default_trading_cost()

    assert cost.commission_rate == 0.0003
    assert cost.commission_min == 5.0
    assert cost.stamp_duty_rate == 0.001
    assert cost.slippage_rate == 0.001


def test_calculate_trading_cost_requires_positive_quantity() -> None:
    """测试股数必须为正数。"""
    cost = get_default_trading_cost()
    with pytest.raises(ValueError, match="quantity must be positive"):
        calculate_trading_cost("000001", "buy", 0, 10.0, cost)


def test_calculate_trading_cost_requires_positive_price() -> None:
    """测试价格必须为正数。"""
    cost = get_default_trading_cost()
    with pytest.raises(ValueError, match="price must be positive"):
        calculate_trading_cost("000001", "buy", 1000, 0.0, cost)


def test_calculate_trading_cost_large_trade() -> None:
    """测试大额交易。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)
    result = calculate_trading_cost("000001", "buy", 100000, 100.0, cost)

    assert result.execution_price == pytest.approx(100.1)  # 100 * (1 + 0.001)
    assert result.commission == pytest.approx(3003.0)  # 10010000 * 0.0003 = 3003.0 >= 5
    assert result.net_value == pytest.approx(-10013003.0)


def test_calculate_trading_cost_small_trade() -> None:
    """测试小额交易。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)
    result = calculate_trading_cost("000001", "buy", 100, 5.0, cost)

    assert result.execution_price == pytest.approx(5.005)  # 5 * (1 + 0.001)
    assert result.commission == 5.0  # 500.5 * 0.0003 = 0.15015 < 5
    assert result.net_value == pytest.approx(-505.5)


def test_calculate_trading_cost_commission_above_min() -> None:
    """测试佣金高于最低值的场景。"""
    cost = TradingCost(commission_rate=0.0003, commission_min=5.0, stamp_duty_rate=0.001, slippage_rate=0.001)
    result = calculate_trading_cost("000001", "buy", 50000, 100.0, cost)

    assert result.execution_price == pytest.approx(100.1)  # 100 * (1 + 0.001)
    assert result.commission == pytest.approx(1501.5)  # 5005000 * 0.0003 = 1501.5 >= 5
    assert result.net_value == pytest.approx(-5006501.5)