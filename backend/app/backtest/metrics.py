from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceMetrics:
    """绩效指标。

    Attributes:
        total_return: 总收益率
        annual_return: 年化收益率
        max_drawdown: 最大回撤
        sharpe_ratio: 夏普比率
        turnover_rate: 换手率
        win_rate: 胜率
    """

    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float | None
    turnover_rate: float
    win_rate: float | None


@dataclass(frozen=True)
class DailyReturn:
    """日收益率数据。

    Attributes:
        date: 日期
        strategy_return: 策略日收益率
        benchmark_return: 基准日收益率
    """

    date: str
    strategy_return: float
    benchmark_return: float | None = None


def calculate_total_return(
    initial_value: float,
    final_value: float,
) -> float:
    """计算总收益率。

    Args:
        initial_value: 初始价值
        final_value: 最终价值

    Returns:
        总收益率
    """
    if initial_value <= 0:
        raise ValueError("initial_value must be positive")
    return (final_value - initial_value) / initial_value


def calculate_annual_return(
    total_return: float,
    days: int,
) -> float:
    """计算年化收益率。

    Args:
        total_return: 总收益率
        days: 天数

    Returns:
        年化收益率
    """
    if days <= 0:
        raise ValueError("days must be positive")
    return (1 + total_return) ** (365 / days) - 1


def calculate_max_drawdown(values: Sequence[float]) -> float:
    """计算最大回撤。

    Args:
        values: 价值序列

    Returns:
        最大回撤
    """
    if not values:
        return 0.0

    peak = values[0]
    max_dd = 0.0

    for value in values:
        if value > peak:
            peak = value
        dd = (peak - value) / peak
        if dd > max_dd:
            max_dd = dd

    return max_dd


def calculate_sharpe_ratio(
    returns: Sequence[float],
    risk_free_rate: float = 0.03,
) -> float:
    """计算夏普比率。

    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率（年化）

    Returns:
        夏普比率
    """
    if not returns:
        raise ValueError("returns cannot be empty")

    if len(returns) == 1:
        return 0.0

    import math

    avg_return = sum(returns) / len(returns)
    variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
    std = math.sqrt(variance)

    if std == 0:
        return 0.0

    daily_rf = risk_free_rate / 365
    return (avg_return - daily_rf) / std


def calculate_turnover_rate(
    buy_volume: float,
    sell_volume: float,
    avg_portfolio_value: float,
) -> float:
    """计算换手率。

    Args:
        buy_volume: 买入总额
        sell_volume: 卖出总额
        avg_portfolio_value: 平均组合价值

    Returns:
        换手率
    """
    if avg_portfolio_value <= 0:
        raise ValueError("avg_portfolio_value must be positive")
    return (buy_volume + sell_volume) / (2 * avg_portfolio_value)


def calculate_win_rate(
    daily_returns: Sequence[DailyReturn],
    benchmark_key: Callable[[DailyReturn], float] | None = None,
) -> float:
    """计算胜率。

    Args:
        daily_returns: 日收益率序列
        benchmark_key: 基准收益率获取函数，None 表示使用 daily_returns 中的 benchmark_return

    Returns:
        胜率
    """
    if not daily_returns:
        return 0.0

    if benchmark_key is None:

        def benchmark_key(dr: DailyReturn) -> float | None:
            return dr.benchmark_return

    valid_returns = [dr for dr in daily_returns if benchmark_key(dr) is not None]
    if not valid_returns:
        return 0.0

    wins = sum(1 for dr in valid_returns if dr.strategy_return > benchmark_key(dr))
    total = len(valid_returns)

    return wins / total if total > 0 else 0.0


def calculate_performance_metrics(
    initial_value: float,
    final_value: float,
    daily_values: Sequence[float],
    daily_returns: Sequence[DailyReturn] | None = None,
    buy_volume: float = 0.0,
    sell_volume: float = 0.0,
    avg_portfolio_value: float = 0.0,
    risk_free_rate: float = 0.03,
) -> PerformanceMetrics:
    """计算绩效指标。

    Args:
        initial_value: 初始价值
        final_value: 最终价值
        daily_values: 日价值序列
        daily_returns: 日收益率序列，用于计算夏普比率和胜率
        buy_volume: 买入总额
        sell_volume: 卖出总额
        avg_portfolio_value: 平均组合价值
        risk_free_rate: 无风险利率

    Returns:
        绩效指标
    """
    total_return = calculate_total_return(initial_value, final_value)
    days = len(daily_values)
    annual_return = calculate_annual_return(total_return, days)
    max_dd = calculate_max_drawdown(daily_values)

    if daily_returns and len(daily_returns) > 1:
        sharpe = calculate_sharpe_ratio(
            [dr.strategy_return for dr in daily_returns],
            risk_free_rate,
        )
    else:
        sharpe = None

    if avg_portfolio_value > 0:
        turnover = calculate_turnover_rate(buy_volume, sell_volume, avg_portfolio_value)
    else:
        turnover = 0.0

    if daily_returns:
        win_rate = calculate_win_rate(daily_returns, lambda dr: dr.benchmark_return)
    else:
        win_rate = None

    return PerformanceMetrics(
        total_return=total_return,
        annual_return=annual_return,
        max_drawdown=max_dd,
        sharpe_ratio=sharpe,
        turnover_rate=turnover,
        win_rate=win_rate,
    )
