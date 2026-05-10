from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    """交易订单。

    Attributes:
        stock_code: 股票代码
        action: 订单动作，"buy" 或 "sell"
        quantity: 股数（100 的倍数）
        price: 执行价格
    """

    stock_code: str
    action: str
    quantity: int
    price: float


def generate_orders(
    target_weights: dict[str, float],
    current_shares: dict[str, int],
    prices: dict[str, float],
    portfolio_value: float,
) -> list[Order]:
    """根据目标仓位和当前持仓生成订单。

    Args:
        target_weights: 股票代码到目标权重的映射，权重和应 <= 1
        current_shares: 股票代码到当前持股数的映射
        prices: 股票代码到当前价格的映射
        portfolio_value: 组合总价值

    Returns:
        订单列表，按股票代码排序

    订单生成规则：
    - 买入数量 = 目标权重 * 组合价值 / 价格，向下取整到 100 股
    - 卖出数量 = 当前持股 - 目标持股，取整到 100 股（四舍五入）
    - 差异小于 50 股时不交易
    """
    if portfolio_value <= 0:
        raise ValueError("portfolio_value must be positive")

    target_value_by_stock = {
        code: weight * portfolio_value for code, weight in target_weights.items()
    }

    target_shares_by_stock = {
        code: int(target_value / prices[code] // 100 * 100)
        for code, target_value in target_value_by_stock.items()
        if code in prices and prices[code] > 0
    }

    orders: list[Order] = []
    processed_codes = set()

    for stock_code, target_shares in target_shares_by_stock.items():
        current_shares_count = current_shares.get(stock_code, 0)
        diff = target_shares - current_shares_count

        if abs(diff) < 50:
            processed_codes.add(stock_code)
            continue

        if diff > 0:
            orders.append(
                Order(
                    stock_code=stock_code,
                    action="buy",
                    quantity=(diff // 100) * 100,
                    price=prices[stock_code],
                )
            )
        else:
            orders.append(
                Order(
                    stock_code=stock_code,
                    action="sell",
                    quantity=(abs(diff) + 50) // 100 * 100,
                    price=prices[stock_code],
                )
            )
        processed_codes.add(stock_code)

    for stock_code, shares in current_shares.items():
        if stock_code not in processed_codes and stock_code in prices:
            if shares >= 50:
                orders.append(
                    Order(
                        stock_code=stock_code,
                        action="sell",
                        quantity=(shares + 50) // 100 * 100,
                        price=prices[stock_code],
                    )
                )

    orders.sort(key=lambda o: o.stock_code)
    return orders
