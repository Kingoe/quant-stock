from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradingCost:
    """交易成本配置。

    Attributes:
        commission_rate: 佣金率，如 0.0003 表示万分之三
        commission_min: 最低佣金
        stamp_duty_rate: 印花税率，仅卖出时收取，如 0.001 表示千分之一
        slippage_rate: 滑点率，如 0.001 表示千分之一
    """

    commission_rate: float = 0.0003
    commission_min: float = 5.0
    stamp_duty_rate: float = 0.001
    slippage_rate: float = 0.001


@dataclass(frozen=True)
class TradeResult:
    """交易结果。

    Attributes:
        stock_code: 股票代码
        action: 订单动作，"buy" 或 "sell"
        quantity: 股数
        price: 原始价格
        execution_price: 执行价格（含滑点）
        commission: 佣金
        stamp_duty: 印花税（仅卖出）
        total_cost: 总成本（佣金 + 印花税 + 滑点成本）
        net_value: 净价值
    """

    stock_code: str
    action: str
    quantity: int
    price: float
    execution_price: float
    commission: float
    stamp_duty: float
    total_cost: float
    net_value: float


def calculate_trading_cost(
    stock_code: str,
    action: str,
    quantity: int,
    price: float,
    cost: TradingCost,
) -> TradeResult:
    """计算交易成本。

    Args:
        stock_code: 股票代码
        action: "buy" 或 "sell"
        quantity: 股数
        price: 原始价格
        cost: 交易成本配置

    Returns:
        交易结果，包含执行价格、佣金、印花税和总成本

    交易成本规则：
    - 佣金 = 成交金额 * 佣金率，且不低于最低佣金
    - 印花税 = 卖出成交金额 * 印花税率，买入无印花税
    - 滑点：买入时价格上涨，卖出时价格下跌
    """
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if price <= 0:
        raise ValueError("price must be positive")

    if action == "buy":
        execution_price = price * (1 + cost.slippage_rate)
    else:
        execution_price = price * (1 - cost.slippage_rate)

    amount = quantity * execution_price

    commission = max(amount * cost.commission_rate, cost.commission_min)

    if action == "sell":
        stamp_duty = amount * cost.stamp_duty_rate
    else:
        stamp_duty = 0.0

    total_cost = commission + stamp_duty

    if action == "buy":
        net_value = -amount - total_cost
    else:
        net_value = amount - total_cost

    return TradeResult(
        stock_code=stock_code,
        action=action,
        quantity=quantity,
        price=price,
        execution_price=execution_price,
        commission=commission,
        stamp_duty=stamp_duty,
        total_cost=total_cost,
        net_value=net_value,
    )


def get_default_trading_cost() -> TradingCost:
    """获取默认交易成本配置。

    Returns:
        默认交易成本配置
        - 佣金率：万分之三
        - 最低佣金：5 元
        - 印花税率：千分之一（仅卖出）
        - 滑点率：千分之一
    """
    return TradingCost(
        commission_rate=0.0003,
        commission_min=5.0,
        stamp_duty_rate=0.001,
        slippage_rate=0.001,
    )
