from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Portfolio:
    """投资组合状态。

    Attributes:
        cash: 现金余额
        positions: 股票代码到持股数的映射
    """
    cash: float
    positions: dict[str, int]

    def __post_init__(self) -> None:
        if self.cash < 0:
            raise ValueError("cash cannot be negative")

        for stock_code, shares in self.positions.items():
            if shares < 0:
                raise ValueError(f"shares for {stock_code} cannot be negative")


@dataclass(frozen=True)
class Position:
    """持仓信息。

    Attributes:
        stock_code: 股票代码
        shares: 持股数
        avg_cost: 平均成本
        market_value: 市值
    """
    stock_code: str
    shares: int
    avg_cost: float
    market_value: float


@dataclass(frozen=True)
class PortfolioSnapshot:
    """投资组合快照。

    Attributes:
        date: 日期
        cash: 现金余额
        positions: 持仓列表
        total_value: 总价值（现金 + 持仓市值）
    """
    date: str
    cash: float
    positions: list[Position]
    total_value: float


def apply_trade(
    portfolio: Portfolio,
    stock_code: str,
    quantity: int,
    price: float,
) -> Portfolio:
    """应用交易到投资组合。

    Args:
        portfolio: 当前投资组合
        stock_code: 股票代码
        quantity: 交易股数（正数为买入，负数为卖出）
        price: 交易价格

    Returns:
        更新后的投资组合
    """
    current_shares = portfolio.positions.get(stock_code, 0)

    if quantity > 0:
        new_shares = current_shares + quantity
        cost = quantity * price
        new_cash = portfolio.cash - cost
    else:
        new_shares = current_shares + quantity  # quantity is negative
        proceeds = abs(quantity) * price
        new_cash = portfolio.cash + proceeds

    new_positions = dict(portfolio.positions)
    if new_shares == 0:
        new_positions.pop(stock_code, None)
    else:
        new_positions[stock_code] = new_shares

    return Portfolio(cash=new_cash, positions=new_positions)


def calculate_position_value(
    portfolio: Portfolio,
    prices: Mapping[str, float],
) -> float:
    """计算持仓市值。

    Args:
        portfolio: 当前投资组合
        prices: 股票代码到价格的映射

    Returns:
        持仓市值
    """
    total_value = 0.0
    for stock_code, shares in portfolio.positions.items():
        if stock_code in prices and shares > 0:
            total_value += shares * prices[stock_code]
    return total_value


def calculate_portfolio_value(
    portfolio: Portfolio,
    prices: Mapping[str, float],
) -> float:
    """计算组合总价值。

    Args:
        portfolio: 当前投资组合
        prices: 股票代码到价格的映射

    Returns:
        组合总价值（现金 + 持仓市值）
    """
    position_value = calculate_position_value(portfolio, prices)
    return portfolio.cash + position_value


def get_position_details(
    portfolio: Portfolio,
    prices: Mapping[str, float],
    avg_costs: Mapping[str, float],
) -> list[Position]:
    """获取持仓详情。

    Args:
        portfolio: 当前投资组合
        prices: 股票代码到当前价格的映射
        avg_costs: 股票代码到平均成本的映射

    Returns:
        持仓详情列表
    """
    positions: list[Position] = []
    for stock_code, shares in portfolio.positions.items():
        if shares > 0:
            price = prices.get(stock_code, 0.0)
            avg_cost = avg_costs.get(stock_code, price)
            market_value = shares * price
            positions.append(
                Position(
                    stock_code=stock_code,
                    shares=shares,
                    avg_cost=avg_cost,
                    market_value=market_value,
                )
            )
    return positions


def create_snapshot(
    date: str,
    portfolio: Portfolio,
    prices: Mapping[str, float],
    avg_costs: Mapping[str, float] | None = None,
) -> PortfolioSnapshot:
    """创建投资组合快照。

    Args:
        date: 日期
        portfolio: 当前投资组合
        prices: 股票代码到价格的映射
        avg_costs: 股票代码到平均成本的映射

    Returns:
        投资组合快照
    """
    if avg_costs is None:
        avg_costs = {}

    positions = get_position_details(portfolio, prices, avg_costs)
    total_value = calculate_portfolio_value(portfolio, prices)

    return PortfolioSnapshot(
        date=date,
        cash=portfolio.cash,
        positions=positions,
        total_value=total_value,
    )


def create_initial_portfolio(initial_cash: float) -> Portfolio:
    """创建初始投资组合。

    Args:
        initial_cash: 初始现金

    Returns:
        初始投资组合
    """
    return Portfolio(cash=initial_cash, positions={})