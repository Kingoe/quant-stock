from __future__ import annotations

from collections.abc import Mapping, Sequence


def calculate_benchmark_return(
    current_index: float,
    previous_index: float,
) -> float:
    """计算基准收益率。

    Args:
        current_index: 当前指数
        previous_index: 前一指数

    Returns:
        基准收益率
    """
    if previous_index <= 0:
        raise ValueError("previous_index must be positive")
    return (current_index - previous_index) / previous_index


def calculate_cumulative_returns(
    values: Sequence[float],
) -> list[float]:
    """计算累计收益率序列。

    Args:
        values: 价值序列

    Returns:
        累计收益率序列
    """
    if not values:
        return []

    returns = []
    initial_value = values[0]

    for value in values:
        if initial_value <= 0:
            raise ValueError("initial value must be positive")
        returns.append((value - initial_value) / initial_value)

    return returns


def calculate_benchmark_cumulative_returns(
    index_values: Mapping[str, float],
    dates: Sequence[str],
) -> list[tuple[str, float]]:
    """计算基准累计收益率。

    Args:
        index_values: 日期到指数值的映射
        dates: 日期序列

    Returns:
        (日期, 累计收益率)列表，按日期排序
    """
    if not dates:
        return []

    first_date = dates[0]
    initial_value = index_values.get(first_date, 0.0)

    if initial_value <= 0:
        raise ValueError(f"initial index value for {first_date} must be positive")

    returns: list[tuple[str, float]] = []
    for date in dates:
        index_value = index_values.get(date, initial_value)
        cumulative_return = (index_value - initial_value) / initial_value
        returns.append((date, cumulative_return))

    return returns


def align_strategy_and_benchmark_dates(
    strategy_dates: Sequence[str],
    benchmark_dates: Sequence[str],
) -> list[str]:
    """对齐策略和基准日期。

    Args:
        strategy_dates: 策略日期序列
        benchmark_dates: 基准日期序列

    Returns:
        对齐后的日期列表（交集）
    """
    strategy_set = set(strategy_dates)
    benchmark_set = set(benchmark_dates)
    aligned = sorted(strategy_set & benchmark_set)
    return aligned