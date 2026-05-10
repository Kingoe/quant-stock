from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class OrderSide(StrEnum):
    """订单方向。"""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(StrEnum):
    """订单状态。"""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Position:
    """持仓记录。"""

    stock_code: str
    shares: int = 0
    avg_cost: Decimal = Decimal("0")
    current_price: Decimal | None = None

    @property
    def market_value(self) -> Decimal:
        """持仓市值。"""
        if self.current_price is None:
            return Decimal("0")
        return Decimal(self.current_price) * Decimal(self.shares)

    @property
    def profit_loss(self) -> Decimal:
        """未实现盈亏。"""
        return self.market_value - (Decimal(self.avg_cost) * Decimal(self.shares))

    @property
    def profit_loss_pct(self) -> Decimal:
        """未实现盈亏百分比。"""
        cost = Decimal(self.avg_cost) * Decimal(self.shares)
        if cost == 0:
            return Decimal("0")
        return self.profit_loss / cost * 100


@dataclass
class Order:
    """订单记录。"""

    order_id: str
    stock_code: str
    side: OrderSide
    quantity: int
    price: Decimal
    status: OrderStatus = OrderStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    filled_at: str | None = None
    filled_quantity: int = 0
    commission: Decimal = Decimal("0")
    message: str | None = None

    @property
    def total_amount(self) -> Decimal:
        """订单金额。"""
        return Decimal(self.price) * Decimal(self.quantity)

    @property
    def filled_amount(self) -> Decimal:
        """已成交金额。"""
        return Decimal(self.price) * Decimal(self.filled_quantity)


@dataclass
class Account:
    """模拟账户。"""

    account_id: str
    initial_cash: Decimal
    cash: Decimal
    positions: dict[str, Position] = field(default_factory=dict)
    total_commission: Decimal = Decimal("0")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def total_value(self) -> Decimal:
        """总资产。"""
        return self.cash + sum(p.market_value for p in self.positions.values())

    @property
    def total_cost(self) -> Decimal:
        """总成本。"""
        return sum(Decimal(p.avg_cost) * Decimal(p.shares) for p in self.positions.values())

    @property
    def total_profit_loss(self) -> Decimal:
        """总盈亏。"""
        return self.total_value - self.initial_cash

    @property
    def total_return(self) -> Decimal:
        """总收益率。"""
        if self.initial_cash == 0:
            return Decimal("0")
        return self.total_profit_loss / self.initial_cash * 100


class SimulationLedger:
    """模拟交易账本。"""

    def __init__(self, account_id: str, initial_cash: float) -> None:
        self.account = Account(
            account_id=account_id,
            initial_cash=Decimal(str(initial_cash)),
            cash=Decimal(str(initial_cash)),
        )
        self.orders: list[Order] = []

    def create_order(
        self,
        stock_code: str,
        side: OrderSide,
        quantity: int,
        price: float,
    ) -> Order:
        """创建订单。

        Args:
            stock_code: 股票代码
            side: 买卖方向
            quantity: 数量（股）
            price: 价格

        Returns:
            创建的订单
        """
        order = Order(
            order_id=self._generate_order_id(),
            stock_code=stock_code,
            side=side,
            quantity=quantity,
            price=Decimal(str(price)),
        )
        self.orders.append(order)
        return order

    def fill_order(
        self,
        order: Order,
        fill_price: float | None = None,
        commission: float = 0.0003,
    ) -> None:
        """成交订单。

        Args:
            order: 要成交的订单
            fill_price: 成交价格，None 则使用订单价格
            commission: 佣金率
        """
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Order {order.order_id} is not pending")

        price = Decimal(str(fill_price)) if fill_price else order.price
        amount = price * Decimal(order.quantity)
        comm = amount * Decimal(str(commission))

        if order.side == OrderSide.BUY:
            total_cost = amount + comm
            if total_cost > self.account.cash:
                order.status = OrderStatus.FAILED
                order.message = "Insufficient cash"
                return

            self.account.cash -= total_cost
            self.account.total_commission += comm
            self._update_position(order.stock_code, order.quantity, price)

        elif order.side == OrderSide.SELL:
            position = self.account.positions.get(order.stock_code)
            if position is None or position.shares < order.quantity:
                order.status = OrderStatus.FAILED
                order.message = "Insufficient position"
                return

            self.account.cash += amount - comm
            self.account.total_commission += comm
            self._update_position(order.stock_code, -order.quantity, price)

        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now().isoformat()
        order.filled_quantity = order.quantity
        order.commission = comm

    def cancel_order(self, order: Order, reason: str | None = None) -> None:
        """取消订单。

        Args:
            order: 要取消的订单
            reason: 取消原因
        """
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Order {order.order_id} is not pending")

        order.status = OrderStatus.CANCELLED
        order.message = reason

    def update_prices(self, prices: dict[str, float]) -> None:
        """更新持仓当前价格。

        Args:
            prices: 股票代码到价格的映射
        """
        for stock_code, price in prices.items():
            if stock_code in self.account.positions:
                self.account.positions[stock_code].current_price = Decimal(str(price))

    def get_position(self, stock_code: str) -> Position | None:
        """获取持仓。

        Args:
            stock_code: 股票代码

        Returns:
            持仓记录，不存在返回 None
        """
        return self.account.positions.get(stock_code)

    def get_orders(
        self,
        stock_code: str | None = None,
        status: OrderStatus | None = None,
    ) -> list[Order]:
        """获取订单列表。

        Args:
            stock_code: 股票代码过滤
            status: 状态过滤

        Returns:
            订单列表
        """
        orders = self.orders
        if stock_code:
            orders = [o for o in orders if o.stock_code == stock_code]
        if status:
            orders = [o for o in orders if o.status == status]
        return orders

    def _generate_order_id(self) -> str:
        """生成订单 ID。"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"SIM{timestamp}{len(self.orders):04d}"

    def _update_position(
        self,
        stock_code: str,
        quantity: int,
        price: Decimal,
    ) -> None:
        """更新持仓。

        Args:
            stock_code: 股票代码
            quantity: 数量（正为买入，负为卖出）
            price: 价格
        """
        if stock_code not in self.account.positions:
            self.account.positions[stock_code] = Position(stock_code=stock_code)

        position = self.account.positions[stock_code]

        if quantity > 0:
            total_cost = position.shares * position.avg_cost + quantity * price
            position.shares += quantity
            position.avg_cost = (
                total_cost / position.shares if position.shares > 0 else Decimal("0")
            )
        else:
            position.shares += quantity
            if position.shares == 0:
                position.avg_cost = Decimal("0")

        if position.shares == 0:
            del self.account.positions[stock_code]
