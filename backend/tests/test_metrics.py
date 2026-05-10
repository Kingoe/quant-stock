from __future__ import annotations

import pytest

from app.backtest.metrics import (
    DailyReturn,
    calculate_annual_return,
    calculate_max_drawdown,
    calculate_performance_metrics,
    calculate_sharpe_ratio,
    calculate_total_return,
    calculate_turnover_rate,
    calculate_win_rate,
)


def test_calculate_total_return() -> None:
    """测试计算总收益率。"""
    assert calculate_total_return(100, 110) == 0.1
    assert calculate_total_return(100, 90) == pytest.approx(-0.1)
    assert calculate_total_return(100, 100) == 0.0


def test_calculate_total_return_requires_positive_initial() -> None:
    """测试初始价值必须为正数。"""
    with pytest.raises(ValueError, match="initial_value must be positive"):
        calculate_total_return(0, 100)


def test_calculate_annual_return() -> None:
    """测试计算年化收益率。"""
    # 10% 的 90 天收益
    annual = calculate_annual_return(0.1, 90)
    assert annual > 0.1  # 年化高于期间收益


def test_calculate_annual_return_requires_positive_days() -> None:
    """测试天数必须为正数。"""
    with pytest.raises(ValueError, match="days must be positive"):
        calculate_annual_return(0.1, 0)


def test_calculate_max_drawdown() -> None:
    """测试计算最大回撤。"""
    values = [100, 110, 90, 95, 85]
    dd = calculate_max_drawdown(values)
    # Peak is 110, lowest is 85, max drawdown is (110 - 85) / 110 = 22.73%
    assert dd == pytest.approx(0.2273, abs=0.0001)


def test_calculate_max_drawdown_empty() -> None:
    """测试空序列返回 0。"""
    assert calculate_max_drawdown([]) == 0.0


def test_calculate_max_drawdown_no_drawdown() -> None:
    """测试无回撤时返回 0。"""
    assert calculate_max_drawdown([100, 110, 120]) == 0.0


def test_calculate_sharpe_ratio() -> None:
    """测试计算夏普比率。"""
    returns = [0.01, -0.005, 0.02, 0.015, -0.01]
    sharpe = calculate_sharpe_ratio(returns)
    assert isinstance(sharpe, float)


def test_calculate_sharpe_ratio_empty() -> None:
    """测试空序列抛出异常。"""
    with pytest.raises(ValueError, match="returns cannot be empty"):
        calculate_sharpe_ratio([])


def test_calculate_sharpe_ratio_single_value() -> None:
    """测试单值返回 0。"""
    assert calculate_sharpe_ratio([0.01]) == 0.0


def test_calculate_sharpe_ratio_zero_variance() -> None:
    """测试零方差时返回 0。"""
    assert calculate_sharpe_ratio([0.01, 0.01, 0.01]) == 0.0


def test_calculate_turnover_rate() -> None:
    """测试计算换手率。"""
    # 买入 10000，卖出 8000，平均组合价值 50000
    # (10000 + 8000) / (2 * 50000) = 18000 / 100000 = 0.18
    turnover = calculate_turnover_rate(10000, 8000, 50000)
    assert turnover == pytest.approx(0.18)


def test_calculate_turnover_rate_requires_positive_avg_value() -> None:
    """测试平均组合价值必须为正数。"""
    with pytest.raises(ValueError, match="avg_portfolio_value must be positive"):
        calculate_turnover_rate(10000, 8000, 0)


def test_calculate_win_rate() -> None:
    """测试计算胜率。"""
    daily_returns = [
        DailyReturn("2026-05-01", 0.01, 0.005),  # 策略胜
        DailyReturn("2026-05-02", -0.01, 0.005),  # 策略负
        DailyReturn("2026-05-03", 0.02, 0.01),  # 策略胜
        DailyReturn("2026-05-04", 0.005, 0.01),  # 策略负
    ]
    win_rate = calculate_win_rate(daily_returns)
    assert win_rate == 0.5  # 2 / 4


def test_calculate_win_rate_empty() -> None:
    """测试空序列返回 0。"""
    assert calculate_win_rate([]) == 0.0


def test_calculate_win_rate_no_benchmark() -> None:
    """测试无基准时返回 0。"""
    daily_returns = [DailyReturn("2026-05-01", 0.01, None)]
    win_rate = calculate_win_rate(daily_returns)
    assert win_rate == 0.0


def test_calculate_performance_metrics() -> None:
    """测试计算绩效指标。"""
    metrics = calculate_performance_metrics(
        initial_value=100000.0,
        final_value=110000.0,
        daily_values=[100000, 105000, 110000],
        daily_returns=[
            DailyReturn("2026-05-01", 0.05, 0.03),
            DailyReturn("2026-05-02", 0.0476, 0.03),
        ],
        buy_volume=10000.0,
        sell_volume=0.0,
        avg_portfolio_value=105000.0,
        risk_free_rate=0.03,
    )

    assert metrics.total_return == 0.1
    assert metrics.annual_return > 0
    assert metrics.max_drawdown >= 0
    assert metrics.sharpe_ratio is not None
    assert metrics.turnover_rate > 0
    assert metrics.win_rate is not None


def test_calculate_performance_metrics_minimal() -> None:
    """测试最小输入计算绩效指标。"""
    metrics = calculate_performance_metrics(
        initial_value=100000.0,
        final_value=110000.0,
        daily_values=[100000, 105000, 110000],
    )

    assert metrics.total_return == 0.1
    assert metrics.annual_return > 0
    assert metrics.max_drawdown == 0.0
    assert metrics.sharpe_ratio is None
    assert metrics.turnover_rate == 0.0
    assert metrics.win_rate is None
