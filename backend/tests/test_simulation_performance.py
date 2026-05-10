from __future__ import annotations

from decimal import Decimal

import pytest

from app.simulation import (
    PortfolioSnapshot,
    analyze_performance,
    calculate_daily_returns,
    calculate_drawdowns,
    create_portfolio_snapshot,
    get_max_drawdown,
    get_sharpe_ratio,
)


def test_create_portfolio_snapshot() -> None:
    """测试创建组合快照。"""
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        snapshot = create_portfolio_snapshot(
            account_id="test_account",
            snapshot_date="2026-05-10",
            cash=50000,
            positions_value=45000,
            initial_cash=100000,
        )

        assert snapshot.account_id == "test_account"
        assert snapshot.snapshot_date == "2026-05-10"
        assert snapshot.cash == 50000
        assert snapshot.total_value == 95000
        assert snapshot.positions_value == 45000
        assert snapshot.total_return == pytest.approx(-5.0)


def test_create_portfolio_snapshot_zero_initial() -> None:
    """测试初始资金为0时的快照创建。"""
    snapshot = create_portfolio_snapshot(
        account_id="test_account",
        snapshot_date="2026-05-10",
        cash=50000,
        positions_value=45000,
        initial_cash=0,
    )

    assert snapshot.total_return == Decimal("0")


def test_calculate_daily_returns() -> None:
    """测试日收益率计算。"""
    snapshots = [
        PortfolioSnapshot(
            id=1,
            account_id="test",
            snapshot_date="2026-05-09",
            cash=100000,
            total_value=Decimal("100000"),
            positions_value=Decimal("0"),
            total_return=Decimal("0"),
            created_at="2026-05-09T00:00:00",
        ),
        PortfolioSnapshot(
            id=2,
            account_id="test",
            snapshot_date="2026-05-10",
            cash=105000,
            total_value=Decimal("105000"),
            positions_value=Decimal("0"),
            total_return=Decimal("5.0"),
            created_at="2026-05-10T00:00:00",
        ),
    ]

    returns = calculate_daily_returns(snapshots)

    assert len(returns) == 1
    assert returns[0][0] == "2026-05-10"
    assert returns[0][1] == pytest.approx(5.0)


def test_calculate_drawdowns() -> None:
    """测试回撤计算。"""
    snapshots = [
        PortfolioSnapshot(
            id=1,
            account_id="test",
            snapshot_date="2026-05-09",
            cash=100000,
            total_value=Decimal("100000"),
            positions_value=Decimal("0"),
            total_return=Decimal("0"),
            created_at="2026-05-09T00:00:00",
        ),
        PortfolioSnapshot(
            id=2,
            account_id="test",
            snapshot_date="2026-05-10",
            cash=90000,
            total_value=Decimal("90000"),
            positions_value=Decimal("0"),
            total_return=Decimal("-10.0"),
            created_at="2026-05-10T00:00:00",
        ),
        PortfolioSnapshot(
            id=3,
            account_id="test",
            snapshot_date="2026-05-11",
            cash=95000,
            total_value=Decimal("95000"),
            positions_value=Decimal("0"),
            total_return=Decimal("-5.0"),
            created_at="2026-05-11T00:00:00",
        ),
    ]

    drawdowns = calculate_drawdowns(snapshots)

    assert len(drawdowns) == 3
    assert drawdowns[0][1] == pytest.approx(0.0)
    assert drawdowns[1][1] == pytest.approx(10.0)
    assert drawdowns[2][1] == pytest.approx(5.0)


def test_get_max_drawdown() -> None:
    """测试获取最大回撤。"""
    snapshots = [
        PortfolioSnapshot(
            id=1,
            account_id="test",
            snapshot_date="2026-05-09",
            cash=100000,
            total_value=Decimal("100000"),
            positions_value=Decimal("0"),
            total_return=Decimal("0"),
            created_at="2026-05-09T00:00:00",
        ),
        PortfolioSnapshot(
            id=2,
            account_id="test",
            snapshot_date="2026-05-10",
            cash=90000,
            total_value=Decimal("90000"),
            positions_value=Decimal("0"),
            total_return=Decimal("-10.0"),
            created_at="2026-05-10T00:00:00",
        ),
    ]

    max_dd = get_max_drawdown(snapshots)

    assert max_dd == pytest.approx(10.0)


def test_get_sharpe_ratio() -> None:
    """测试夏普比率计算。"""
    snapshots = [
        PortfolioSnapshot(
            id=1,
            account_id="test",
            snapshot_date="2026-05-09",
            cash=100000,
            total_value=Decimal("100000"),
            positions_value=Decimal("0"),
            total_return=Decimal("0"),
            created_at="2026-05-09T00:00:00",
        ),
        PortfolioSnapshot(
            id=2,
            account_id="test",
            snapshot_date="2026-05-10",
            cash=101000,
            total_value=Decimal("101000"),
            positions_value=Decimal("0"),
            total_return=Decimal("1.0"),
            created_at="2026-05-10T00:00:00",
        ),
        PortfolioSnapshot(
            id=3,
            account_id="test",
            snapshot_date="2026-05-11",
            cash=103000,
            total_value=Decimal("103000"),
            positions_value=Decimal("0"),
            total_return=Decimal("3.0"),
            created_at="2026-05-11T00:00:00",
        ),
    ]

    sharpe_ratio = get_sharpe_ratio(snapshots, risk_free_rate=0.03)

    assert sharpe_ratio is not None
    assert sharpe_ratio > 0


def test_get_sharpe_ratio_insufficient_data() -> None:
    """测试数据不足时返回 None。"""
    snapshots = [
        PortfolioSnapshot(
            id=1,
            account_id="test",
            snapshot_date="2026-05-09",
            cash=100000,
            total_value=Decimal("100000"),
            positions_value=Decimal("0"),
            total_return=Decimal("0"),
            created_at="2026-05-09T00:00:00",
        ),
    ]

    sharpe_ratio = get_sharpe_ratio(snapshots, risk_free_rate=0.03)

    assert sharpe_ratio is None


def test_analyze_performance() -> None:
    """测试绩效分析。"""
    snapshots = [
        PortfolioSnapshot(
            id=1,
            account_id="test",
            snapshot_date="2026-05-09",
            cash=100000,
            total_value=Decimal("100000"),
            positions_value=Decimal("0"),
            total_return=Decimal("0"),
            created_at="2026-05-09T00:00:00",
        ),
        PortfolioSnapshot(
            id=2,
            account_id="test",
            snapshot_date="2026-05-10",
            cash=105000,
            total_value=Decimal("105000"),
            positions_value=Decimal("0"),
            total_return=Decimal("5.0"),
            created_at="2026-05-10T00:00:00",
        ),
        PortfolioSnapshot(
            id=3,
            account_id="test",
            snapshot_date="2026-05-11",
            cash=100000,
            total_value=Decimal("100000"),
            positions_value=Decimal("0"),
            total_return=Decimal("0"),
            created_at="2026-05-11T00:00:00",
        ),
    ]

    performance = analyze_performance(snapshots)

    assert performance["total_return"] == pytest.approx(0.0)
    assert performance["max_drawdown"] == pytest.approx(4.7619047619)
    assert performance["sharpe_ratio"] == pytest.approx(0.2464018279)
    assert performance["daily_volatility"] == pytest.approx(6.9027090544)


def test_analyze_performance_empty_snapshots() -> None:
    """测试空快照时的绩效分析。"""
    performance = analyze_performance([])

    assert performance["total_return"] == 0
    assert performance["max_drawdown"] == 0
    assert performance["sharpe_ratio"] is None
    assert performance["daily_volatility"] == 0
