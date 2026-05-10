from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class PortfolioSnapshot:
    """组合快照。"""

    id: int | None = None
    account_id: str = ""
    snapshot_date: str = ""
    cash: Decimal = Decimal("0")
    total_value: Decimal = Decimal("0")
    positions_value: Decimal = Decimal("0")
    total_return: Decimal = Decimal("0")
    created_at: str = ""


def create_portfolio_snapshot(
    account_id: str,
    snapshot_date: str,
    cash: float,
    positions_value: float,
    initial_cash: float,
) -> PortfolioSnapshot:
    """创建组合快照。

    Args:
        account_id: 账户 ID
        snapshot_date: 快照日期
        cash: 现金
        positions_value: 持仓市值
        initial_cash: 初始资金

    Returns:
        组合快照
    """
    total_value = Decimal(str(cash)) + Decimal(str(positions_value))
    total_return = (
        (total_value - Decimal(str(initial_cash))) / Decimal(str(initial_cash)) * 100
        if initial_cash > 0
        else Decimal("0")
    )

    return PortfolioSnapshot(
        account_id=account_id,
        snapshot_date=snapshot_date,
        cash=Decimal(str(cash)),
        total_value=total_value,
        positions_value=Decimal(str(positions_value)),
        total_return=total_return,
        created_at=datetime.now().isoformat(),
    )


def calculate_daily_returns(snapshots: list[PortfolioSnapshot]) -> list[tuple[str, float]]:
    """计算日收益率。

    Args:
        snapshots: 快照列表（按日期排序）

    Returns:
        日期和日收益率列表
    """
    if len(snapshots) < 2:
        return []

    returns = []
    for i in range(1, len(snapshots)):
        prev_value = float(snapshots[i - 1].total_value)
        curr_value = float(snapshots[i].total_value)
        daily_return = (curr_value / prev_value - 1) * 100 if prev_value > 0 else 0
        returns.append((snapshots[i].snapshot_date, daily_return))

    return returns


def calculate_drawdowns(snapshots: list[PortfolioSnapshot]) -> list[tuple[str, float]]:
    """计算回撤。

    Args:
        snapshots: 快照列表（按日期排序）

    Returns:
        日期和回撤列表
    """
    if not snapshots:
        return []

    peak = float(snapshots[0].total_value)
    drawdowns = []

    for snapshot in snapshots:
        value = float(snapshot.total_value)
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak * 100 if peak > 0 else 0
        drawdowns.append((snapshot.snapshot_date, drawdown))

    return drawdowns


def get_max_drawdown(snapshots: list[PortfolioSnapshot]) -> float:
    """获取最大回撤。

    Args:
        snapshots: 快照列表

    Returns:
        最大回撤
    """
    drawdowns = calculate_drawdowns(snapshots)
    if not drawdowns:
        return 0.0
    return max(dd[1] for dd in drawdowns)


def get_sharpe_ratio(
    snapshots: list[PortfolioSnapshot],
    risk_free_rate: float = 0.03,
) -> float | None:
    """计算夏普比率。

    Args:
        snapshots: 快照列表
        risk_free_rate: 无风险利率（年化）

    Returns:
        夏普比率，数据不足返回 None
    """
    if len(snapshots) < 2:
        return None

    returns = calculate_daily_returns(snapshots)
    if not returns:
        return None

    daily_returns = [r[1] for r in returns]
    avg_return = sum(daily_returns) / len(daily_returns)

    if len(daily_returns) < 2:
        return None

    variance = sum((r - avg_return) ** 2 for r in daily_returns) / (len(daily_returns) - 1)

    if variance == 0:
        return None

    std_dev = math.sqrt(variance)

    annualized_return = avg_return * 252
    annualized_std = std_dev * math.sqrt(252)
    excess_return = annualized_return - risk_free_rate * 100

    return excess_return / annualized_std if annualized_std > 0 else None


def analyze_performance(snapshots: list[PortfolioSnapshot]) -> dict[str, Any]:
    """分析组合绩效。

    Args:
        snapshots: 快照列表（按日期排序）

    Returns:
        绩效分析结果
    """
    if not snapshots:
        return {
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": None,
            "daily_volatility": 0.0,
            "win_days": 0,
            "loss_days": 0,
            "win_rate": 0.0,
        }

    initial_value = float(snapshots[0].total_value)
    final_value = float(snapshots[-1].total_value)

    total_return = (final_value / initial_value - 1) * 100 if initial_value > 0 else 0
    max_drawdown = get_max_drawdown(snapshots)
    sharpe_ratio = get_sharpe_ratio(snapshots)

    daily_returns = calculate_daily_returns(snapshots)
    if daily_returns:
        avg_return = sum(r[1] for r in daily_returns) / len(daily_returns)
        variance = sum((r[1] - avg_return) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
        daily_volatility = math.sqrt(variance)
    else:
        daily_volatility = 0.0

    win_days = sum(1 for r in daily_returns if r[1] > 0)
    loss_days = sum(1 for r in daily_returns if r[1] <= 0)
    win_rate = win_days / len(daily_returns) if daily_returns else 0

    return {
        "total_return": total_return,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "daily_volatility": daily_volatility,
        "win_days": win_days,
        "loss_days": loss_days,
        "win_rate": win_rate,
    }
