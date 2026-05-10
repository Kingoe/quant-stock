from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradingConstraints:
    """交易约束。

    Attributes:
        t_plus_one: T+1 限制，当日买入的股票不能当日卖出
        limit_up: 涨停日不能买入
        limit_down: 跌停日不能卖出
        suspended: 停牌日不能交易
    """
    t_plus_one: bool = True
    limit_up: bool = True
    limit_down: bool = True
    suspended: bool = True


@dataclass(frozen=True)
class TradingDayStatus:
    """交易日状态。

    Attributes:
        is_limit_up: 是否涨停
        is_limit_down: 是否跌停
        is_suspended: 是否停牌
    """
    is_limit_up: bool = False
    is_limit_down: bool = False
    is_suspended: bool = False


def filter_orders_by_trading_constraints(
    orders: list[tuple[str, str, int, float]],
    trading_day_status: dict[str, TradingDayStatus],
    buy_stocks_today: set[str] | None = None,
    constraints: TradingConstraints | None = None,
) -> list[tuple[str, str, int, float]]:
    """根据交易约束过滤订单。

    Args:
        orders: 订单列表，每个订单为 (stock_code, action, quantity, price)
        trading_day_status: 股票代码到交易日状态的映射
        buy_stocks_today: 今日买入的股票集合，用于 T+1 检查
        constraints: 交易约束配置

    Returns:
        过滤后的订单列表

    交易约束规则：
    - T+1：当日买入的股票不能当日卖出
    - 涨停：涨停日不能买入
    - 跌停：跌停日不能卖出
    - 停牌：停牌日不能交易
    """
    if constraints is None:
        constraints = TradingConstraints()
    if buy_stocks_today is None:
        buy_stocks_today = set()

    filtered: list[tuple[str, str, int, float]] = []
    for stock_code, action, quantity, price in orders:
        status = trading_day_status.get(stock_code, TradingDayStatus())

        if constraints.suspended and status.is_suspended:
            continue

        if constraints.t_plus_one and action == "sell" and stock_code in buy_stocks_today:
            continue

        if constraints.limit_up and action == "buy" and status.is_limit_up:
            continue

        if constraints.limit_down and action == "sell" and status.is_limit_down:
            continue

        filtered.append((stock_code, action, quantity, price))

    return filtered


def get_default_trading_constraints() -> TradingConstraints:
    """获取默认交易约束。

    Returns:
        默认交易约束，包含 T+1、涨停、跌停、停牌所有限制
    """
    return TradingConstraints(
        t_plus_one=True,
        limit_up=True,
        limit_down=True,
        suspended=True,
    )