from __future__ import annotations

import pytest

from app.backtest.benchmark import (
    align_strategy_and_benchmark_dates,
    calculate_benchmark_cumulative_returns,
    calculate_benchmark_return,
    calculate_cumulative_returns,
)


def test_calculate_benchmark_return() -> None:
    """测试计算基准收益率。"""
    assert calculate_benchmark_return(3000, 3000) == 0.0
    assert calculate_benchmark_return(3300, 3000) == 0.1
    assert calculate_benchmark_return(2700, 3000) == pytest.approx(-0.1)


def test_calculate_benchmark_return_requires_positive_previous() -> None:
    """测试前一指数必须为正数。"""
    with pytest.raises(ValueError, match="previous_index must be positive"):
        calculate_benchmark_return(3300, 0)


def test_calculate_cumulative_returns() -> None:
    """测试计算累计收益率序列。"""
    values = [1000, 1100, 950, 1050]
    returns = calculate_cumulative_returns(values)

    assert len(returns) == 4
    assert returns[0] == 0.0
    assert returns[1] == 0.1
    assert returns[2] == pytest.approx(-0.05)
    assert returns[3] == 0.05


def test_calculate_cumulative_returns_empty() -> None:
    """测试空序列返回空列表。"""
    assert calculate_cumulative_returns([]) == []


def test_calculate_cumulative_returns_negative_initial() -> None:
    """测试初始价值为负数时抛出异常。"""
    with pytest.raises(ValueError, match="initial value must be positive"):
        calculate_cumulative_returns([-1000, -900])


def test_calculate_benchmark_cumulative_returns() -> None:
    """测试计算基准累计收益率。"""
    index_values = {
        "2026-05-01": 3000.0,
        "2026-05-02": 3050.0,
        "2026-05-03": 2950.0,
        "2026-05-04": 3025.0,
    }
    dates = ["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"]

    returns = calculate_benchmark_cumulative_returns(index_values, dates)

    assert len(returns) == 4
    assert returns[0][0] == "2026-05-01"
    assert returns[0][1] == 0.0
    assert returns[1][0] == "2026-05-02"
    assert returns[1][1] == pytest.approx(0.01667, abs=0.0001)
    assert returns[2][1] == pytest.approx(-0.01667, abs=0.0001)


def test_calculate_benchmark_cumulative_returns_empty() -> None:
    """测试空日期返回空列表。"""
    returns = calculate_benchmark_cumulative_returns({}, [])
    assert returns == []


def test_calculate_benchmark_cumulative_returns_negative_initial() -> None:
    """测试初始价值为负数时抛出异常。"""
    index_values = {"2026-05-01": -100.0}
    dates = ["2026-05-01"]

    with pytest.raises(ValueError, match="initial index value"):
        calculate_benchmark_cumulative_returns(index_values, dates)


def test_calculate_benchmark_cumulative_returns_missing_initial() -> None:
    """测试缺失初始值时抛出异常。"""
    index_values = {
        "2026-05-02": 3050.0,
        "2026-05-03": 2950.0,
    }
    dates = ["2026-05-01", "2026-05-02", "2026-05-03"]

    # 缺失初始值且使用默认值 0 时应抛出异常
    with pytest.raises(ValueError, match="initial index value"):
        calculate_benchmark_cumulative_returns(index_values, dates)


def test_calculate_benchmark_cumulative_returns_missing_non_initial() -> None:
    """测试非初始值缺失时使用前一值。"""
    index_values = {
        "2026-05-01": 3000.0,
        "2026-05-03": 2950.0,  # 2026-05-02 缺失
    }
    dates = ["2026-05-01", "2026-05-02", "2026-05-03"]

    returns = calculate_benchmark_cumulative_returns(index_values, dates)

    assert len(returns) == 3
    # 2026-05-02 缺失时使用前一值 3000
    assert returns[1][1] == pytest.approx(0.0)


def test_align_strategy_and_benchmark_dates() -> None:
    """测试对齐策略和基准日期。"""
    strategy_dates = ["2026-05-01", "2026-05-02", "2026-05-03"]
    benchmark_dates = ["2026-05-01", "2026-05-03", "2026-05-04"]

    aligned = align_strategy_and_benchmark_dates(strategy_dates, benchmark_dates)

    assert aligned == ["2026-05-01", "2026-05-03"]


def test_align_strategy_and_benchmark_dates_empty() -> None:
    """测试空输入返回空列表。"""
    assert align_strategy_and_benchmark_dates([], []) == []
    assert align_strategy_and_benchmark_dates(["2026-05-01"], []) == []
    assert align_strategy_and_benchmark_dates([], ["2026-05-01"]) == []


def test_align_strategy_and_benchmark_dates_no_overlap() -> None:
    """测试无交集时返回空列表。"""
    strategy_dates = ["2026-05-01", "2026-05-02"]
    benchmark_dates = ["2026-05-03", "2026-05-04"]

    assert align_strategy_and_benchmark_dates(strategy_dates, benchmark_dates) == []
