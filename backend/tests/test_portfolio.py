from __future__ import annotations

import pytest

from app.backtest.portfolio import (
    Portfolio,
    PortfolioSnapshot,
    Position,
    apply_trade,
    calculate_portfolio_value,
    calculate_position_value,
    create_initial_portfolio,
    create_snapshot,
    get_position_details,
)


def test_create_initial_portfolio() -> None:
    """测试创建初始投资组合。"""
    portfolio = create_initial_portfolio(100000.0)
    assert portfolio.cash == 100000.0
    assert portfolio.positions == {}


def test_apply_trade_buy() -> None:
    """测试买入交易。"""
    portfolio = create_initial_portfolio(100000.0)
    updated = apply_trade(portfolio, "000001", 1000, 10.0)

    assert updated.cash == 90000.0
    assert updated.positions == {"000001": 1000}


def test_apply_trade_sell() -> None:
    """测试卖出交易。"""
    portfolio = Portfolio(cash=0.0, positions={"000001": 1000})
    updated = apply_trade(portfolio, "000001", -500, 10.0)

    assert updated.cash == 5000.0
    assert updated.positions == {"000001": 500}


def test_apply_trade_sell_all() -> None:
    """测试全部卖出。"""
    portfolio = Portfolio(cash=0.0, positions={"000001": 1000})
    updated = apply_trade(portfolio, "000001", -1000, 10.0)

    assert updated.cash == 10000.0
    assert updated.positions == {}


def test_apply_trade_new_stock() -> None:
    """测试买入新股票。"""
    portfolio = Portfolio(cash=50000.0, positions={"000001": 1000})
    updated = apply_trade(portfolio, "000002", 500, 20.0)

    assert updated.cash == 40000.0
    assert updated.positions == {"000001": 1000, "000002": 500}


def test_calculate_position_value() -> None:
    """测试计算持仓市值。"""
    portfolio = Portfolio(cash=100000.0, positions={"000001": 1000, "000002": 500})
    prices = {"000001": 10.0, "000002": 20.0}

    value = calculate_position_value(portfolio, prices)

    assert value == 20000.0  # 1000 * 10 + 500 * 20


def test_calculate_position_value_missing_price() -> None:
    """测试缺失价格时忽略该股票。"""
    portfolio = Portfolio(cash=100000.0, positions={"000001": 1000, "000002": 500})
    prices = {"000001": 10.0}

    value = calculate_position_value(portfolio, prices)

    assert value == 10000.0  # 仅 000001 有价格


def test_calculate_portfolio_value() -> None:
    """测试计算组合总价值。"""
    portfolio = Portfolio(cash=80000.0, positions={"000001": 1000})
    prices = {"000001": 10.0}

    total_value = calculate_portfolio_value(portfolio, prices)

    assert total_value == 90000.0  # 80000 + 1000 * 10


def test_get_position_details() -> None:
    """测试获取持仓详情。"""
    portfolio = Portfolio(cash=80000.0, positions={"000001": 1000})
    prices = {"000001": 10.0}
    avg_costs = {"000001": 9.0}

    positions = get_position_details(portfolio, prices, avg_costs)

    assert len(positions) == 1
    assert positions[0].stock_code == "000001"
    assert positions[0].shares == 1000
    assert positions[0].avg_cost == 9.0
    assert positions[0].market_value == 10000.0


def test_get_position_details_missing_avg_cost() -> None:
    """测试缺失平均成本时使用当前价格。"""
    portfolio = Portfolio(cash=80000.0, positions={"000001": 1000})
    prices = {"000001": 10.0}
    avg_costs = {}

    positions = get_position_details(portfolio, prices, avg_costs)

    assert positions[0].avg_cost == 10.0


def test_create_snapshot() -> None:
    """测试创建快照。"""
    portfolio = Portfolio(cash=80000.0, positions={"000001": 1000})
    prices = {"000001": 10.0}
    avg_costs = {"000001": 9.0}

    snapshot = create_snapshot("2026-05-10", portfolio, prices, avg_costs)

    assert snapshot.date == "2026-05-10"
    assert snapshot.cash == 80000.0
    assert len(snapshot.positions) == 1
    assert snapshot.positions[0].stock_code == "000001"
    assert snapshot.positions[0].shares == 1000
    assert snapshot.positions[0].avg_cost == 9.0
    assert snapshot.positions[0].market_value == 10000.0
    assert snapshot.total_value == 90000.0


def test_portfolio_validates_negative_cash() -> None:
    """测试负现金抛出异常。"""
    with pytest.raises(ValueError, match="cash cannot be negative"):
        Portfolio(cash=-1000.0, positions={})


def test_portfolio_validates_negative_shares() -> None:
    """测试负持股数抛出异常。"""
    with pytest.raises(ValueError, match="shares for 000001 cannot be negative"):
        Portfolio(cash=100000.0, positions={"000001": -100})


def test_apply_trade_multiple_trades() -> None:
    """测试连续交易。"""
    portfolio = create_initial_portfolio(100000.0)
    portfolio = apply_trade(portfolio, "000001", 1000, 10.0)
    portfolio = apply_trade(portfolio, "000002", 500, 20.0)
    portfolio = apply_trade(portfolio, "000001", -200, 11.0)

    assert portfolio.cash == 82200.0  # 100000 - 10000 - 10000 + 2200 = 82200
    assert portfolio.positions == {"000001": 800, "000002": 500}


def test_create_snapshot_without_avg_costs() -> None:
    """测试不提供平均成本时创建快照。"""
    portfolio = Portfolio(cash=80000.0, positions={"000001": 1000})
    prices = {"000001": 10.0}

    snapshot = create_snapshot("2026-05-10", portfolio, prices)

    assert snapshot.positions[0].avg_cost == 10.0  # 使用当前价格


def test_calculate_position_value_empty_positions() -> None:
    """测试空持仓时市值为 0。"""
    portfolio = Portfolio(cash=100000.0, positions={})
    prices = {}

    value = calculate_position_value(portfolio, prices)

    assert value == 0.0


def test_calculate_portfolio_value_empty_positions() -> None:
    """测试空持仓时组合价值等于现金。"""
    portfolio = Portfolio(cash=100000.0, positions={})
    prices = {}

    total_value = calculate_portfolio_value(portfolio, prices)

    assert total_value == 100000.0