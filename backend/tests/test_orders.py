from __future__ import annotations

import pytest

from app.backtest.orders import generate_orders


def test_generate_orders_creates_buy_order() -> None:
    """测试生成买入订单。"""
    target_weights = {"000001": 0.5}
    current_shares = {}
    prices = {"000001": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 1
    assert orders[0].stock_code == "000001"
    assert orders[0].action == "buy"
    assert orders[0].quantity == 500
    assert orders[0].price == 10.0


def test_generate_orders_creates_sell_order() -> None:
    """测试生成卖出订单。"""
    target_weights = {}
    current_shares = {"000001": 1000}
    prices = {"000001": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 1
    assert orders[0].stock_code == "000001"
    assert orders[0].action == "sell"
    assert orders[0].quantity == 1000
    assert orders[0].price == 10.0


def test_generate_orders_handles_rebalance() -> None:
    """测试调仓场景。"""
    target_weights = {"000001": 0.6}
    current_shares = {"000001": 400}
    prices = {"000001": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 1
    assert orders[0].stock_code == "000001"
    assert orders[0].action == "buy"
    assert orders[0].quantity == 200


def test_generate_orders_rounds_to_hundreds() -> None:
    """测试股数按 100 股整数手处理。"""
    target_weights = {"000001": 0.555}
    current_shares = {}
    prices = {"000001": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 1
    assert orders[0].quantity % 100 == 0
    assert orders[0].quantity == 500


def test_generate_orders_skips_small_diff() -> None:
    """测试差异小于 50 股时不交易。"""
    target_weights = {"000001": 0.504}
    current_shares = {"000001": 500}
    prices = {"000001": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 0


def test_generate_orders_returns_empty_for_empty_inputs() -> None:
    """测试空输入返回空列表。"""
    orders = generate_orders({}, {}, {}, 10000.0)
    assert orders == []


def test_generate_orders_multiple_stocks() -> None:
    """测试多股票场景。"""
    target_weights = {"000001": 0.3, "000002": 0.3}
    current_shares = {"000001": 100, "000002": 200}
    prices = {"000001": 10.0, "000002": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 2
    assert orders[0].stock_code == "000001"
    assert orders[0].action == "buy"
    assert orders[0].quantity == 200
    assert orders[1].stock_code == "000002"
    assert orders[1].action == "buy"
    assert orders[1].quantity == 100


def test_generate_orders_sorts_by_stock_code() -> None:
    """测试订单按股票代码排序。"""
    target_weights = {"000002": 0.2, "000001": 0.2}
    current_shares = {}
    prices = {"000001": 10.0, "000002": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 2
    assert orders[0].stock_code == "000001"
    assert orders[1].stock_code == "000002"


def test_generate_orders_requires_positive_portfolio_value() -> None:
    """测试组合价值必须为正数。"""
    with pytest.raises(ValueError, match="portfolio_value must be positive"):
        generate_orders({}, {}, {}, 0.0)


def test_generate_orders_ignores_missing_prices() -> None:
    """测试忽略缺少价格的股票。"""
    target_weights = {"000001": 0.2}
    current_shares = {}
    prices = {}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 0


def test_generate_orders_ignores_zero_price() -> None:
    """测试忽略价格为 0 的股票。"""
    target_weights = {"000001": 0.2}
    current_shares = {}
    prices = {"000001": 0.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 0


def test_generate_orders_sells_small_holding() -> None:
    """测试卖出小于 50 股的持仓时四舍五入卖出 100 股。"""
    target_weights = {}
    current_shares = {"000001": 60}
    prices = {"000001": 10.0}
    portfolio_value = 10000.0

    orders = generate_orders(target_weights, current_shares, prices, portfolio_value)

    assert len(orders) == 1
    assert orders[0].stock_code == "000001"
    assert orders[0].action == "sell"
    assert orders[0].quantity == 100
