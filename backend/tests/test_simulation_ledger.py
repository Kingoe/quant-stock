from __future__ import annotations

from decimal import Decimal

import pytest


def test_simulation_ledger_init() -> None:
    """测试模拟交易账本初始化。"""
    from app.simulation import SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    assert ledger.account.account_id == "test_account"
    assert ledger.account.initial_cash == 1000000
    assert ledger.account.cash == 1000000
    assert ledger.account.total_value == 1000000
    assert len(ledger.orders) == 0


def test_create_order() -> None:
    """测试创建订单。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)

    assert order.order_id.startswith("SIM")
    assert order.stock_code == "000001"
    assert order.side == OrderSide.BUY
    assert order.quantity == 100
    assert order.price == 10.50
    assert order.status.value == "pending"
    assert len(ledger.orders) == 1


def test_fill_buy_order() -> None:
    """测试成交买入订单。"""
    from app.simulation import OrderSide, OrderStatus, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    assert order.status == OrderStatus.FILLED
    assert order.filled_quantity == 100
    assert ledger.account.cash < 1000000
    assert "000001" in ledger.account.positions
    position = ledger.get_position("000001")
    assert position.shares == 100
    assert position.avg_cost == 10.50


def test_fill_sell_order() -> None:
    """测试成交卖出订单。"""
    from app.simulation import OrderSide, OrderStatus, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    # 先买入
    buy_order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(buy_order)

    # 再卖出
    sell_order = ledger.create_order("000001", OrderSide.SELL, 50, 11.00)
    ledger.fill_order(sell_order)

    assert sell_order.status == OrderStatus.FILLED
    assert ledger.account.cash > 1000000 - 100 * 10.50
    position = ledger.get_position("000001")
    assert position.shares == 50


def test_fill_order_insufficient_cash() -> None:
    """测试资金不足时订单失败。"""
    from app.simulation import OrderSide, OrderStatus, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    assert order.status == OrderStatus.FAILED
    assert order.message == "Insufficient cash"
    assert ledger.account.cash == 1000
    assert "000001" not in ledger.account.positions


def test_fill_order_insufficient_position() -> None:
    """测试持仓不足时订单失败。"""
    from app.simulation import OrderSide, OrderStatus, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.SELL, 100, 10.50)
    ledger.fill_order(order)

    assert order.status == OrderStatus.FAILED
    assert order.message == "Insufficient position"


def test_cancel_order() -> None:
    """测试取消订单。"""
    from app.simulation import OrderSide, OrderStatus, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.cancel_order(order, reason="User cancelled")

    assert order.status == OrderStatus.CANCELLED
    assert order.message == "User cancelled"


def test_cancel_non_pending_order() -> None:
    """测试取消非待处理订单时抛出异常。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    with pytest.raises(ValueError, match="is not pending"):
        ledger.cancel_order(order)


def test_update_prices() -> None:
    """测试更新持仓价格。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    ledger.update_prices({"000001": 12.00})

    position = ledger.get_position("000001")
    assert position.current_price == 12.00
    assert position.profit_loss == 150


def test_position_market_value() -> None:
    """测试持仓市值计算。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    ledger.update_prices({"000001": 12.00})

    position = ledger.get_position("000001")
    assert position.market_value == 1200


def test_position_profit_loss_pct() -> None:
    """测试持仓盈亏百分比计算。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    ledger.update_prices({"000001": 12.00})

    position = ledger.get_position("000001")
    profit_pct = (150 / 1050) * 100
    assert float(position.profit_loss_pct) == pytest.approx(profit_pct)


def test_account_total_value() -> None:
    """测试账户总资产计算。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    ledger.update_prices({"000001": 12.00})

    total_value = float(ledger.account.total_value)
    expected_cash = 1000000 - 1050 - 0.315
    expected_value = expected_cash + 1200
    assert total_value == pytest.approx(expected_value)


def test_account_total_return() -> None:
    """测试账户总收益率计算。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order)

    ledger.update_prices({"000001": 12.00})

    total_return = float(ledger.account.total_return)
    expected_value = 1000000 - 1050 - 0.315 + 1200
    expected_return = (expected_value - 1000000) / 1000000 * 100
    assert total_return == pytest.approx(expected_return)


def test_get_orders_filtered_by_stock_code() -> None:
    """测试按股票代码筛选订单。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.create_order("000002", OrderSide.BUY, 100, 10.50)
    ledger.create_order("000001", OrderSide.SELL, 50, 11.00)

    orders = ledger.get_orders(stock_code="000001")

    assert len(orders) == 2
    assert all(o.stock_code == "000001" for o in orders)


def test_get_orders_filtered_by_status() -> None:
    """测试按状态筛选订单。"""
    from app.simulation import OrderSide, OrderStatus, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    order1 = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.create_order("000002", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(order1)

    orders = ledger.get_orders(status=OrderStatus.FILLED)

    assert len(orders) == 1
    assert orders[0].order_id == order1.order_id


def test_sell_all_position() -> None:
    """测试卖出全部持仓。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    buy_order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(buy_order)

    sell_order = ledger.create_order("000001", OrderSide.SELL, 100, 11.00)
    ledger.fill_order(sell_order)

    assert "000001" not in ledger.account.positions


def test_commission_calculation() -> None:
    """测试佣金计算。"""
    from app.simulation import OrderSide, SimulationLedger

    ledger = SimulationLedger(account_id="test_account", initial_cash=1000000)

    buy_order = ledger.create_order("000001", OrderSide.BUY, 100, 10.50)
    ledger.fill_order(buy_order, commission=0.0003)

    assert ledger.account.total_commission > 0
    expected_commission = Decimal("100") * Decimal("10.50") * Decimal("0.0003")
    assert ledger.account.total_commission == expected_commission
