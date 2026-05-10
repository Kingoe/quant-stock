from __future__ import annotations

from app.backtest.metrics import calculate_performance_metrics
from app.backtest.portfolio import PortfolioSnapshot
from app.storage import open_sqlite_connection


def get_backtest_summary(
    database_url: str,
    run_id: str,
    risk_free_rate: float = 0.03,
) -> dict:
    """获取回测概览。

    Args:
        database_url: 数据库 URL
        run_id: 回测运行 ID
        risk_free_rate: 无风险利率

    Returns:
        概览数据，包含 core_metrics
    """
    with open_sqlite_connection(database_url) as connection:
        snapshots = _load_portfolio_snapshots(connection, run_id)

    if not snapshots:
        return {
            "data": {
                "core_metrics": {
                    "total_return": 0.0,
                    "annual_return": 0.0,
                    "max_drawdown": 0.0,
                    "sharpe_ratio": None,
                    "turnover_rate": 0.0,
                    "win_rate": None,
                }
            },
            "meta": {},
        }

    values = [s.total_value for s in snapshots]

    initial_value = values[0]
    final_value = values[-1]

    metrics = calculate_performance_metrics(
        initial_value=initial_value,
        final_value=final_value,
        daily_values=values,
        buy_volume=0.0,
        sell_volume=0.0,
        avg_portfolio_value=sum(values) / len(values),
        risk_free_rate=risk_free_rate,
    )

    return {
        "data": {
            "core_metrics": {
                "total_return": round(metrics.total_return, 4),
                "annual_return": round(metrics.annual_return, 4),
                "max_drawdown": round(metrics.max_drawdown, 4),
                "sharpe_ratio": round(metrics.sharpe_ratio, 4)
                if metrics.sharpe_ratio is not None
                else None,
                "turnover_rate": round(metrics.turnover_rate, 4),
                "win_rate": round(metrics.win_rate, 4) if metrics.win_rate is not None else None,
            }
        },
        "meta": {},
    }


def get_equity_curve(
    database_url: str,
    run_id: str,
) -> dict:
    """获取净值曲线。

    Args:
        database_url: 数据库 URL
        run_id: 回测运行 ID

    Returns:
        净值曲线数据，包含 equity_curve（日期, 净值）列表
    """
    with open_sqlite_connection(database_url) as connection:
        snapshots = _load_portfolio_snapshots(connection, run_id)

    equity_curve = [(s.date, round(s.total_value, 2)) for s in snapshots]

    return {
        "data": {"equity_curve": equity_curve},
        "meta": {},
    }


def get_drawdown_curve(
    database_url: str,
    run_id: str,
) -> dict:
    """获取回撤曲线。

    Args:
        database_url: 数据库 URL
        run_id: 回测运行 ID

    Returns:
        回撤曲线数据，包含 drawdown（日期, 回撤）列表
    """
    with open_sqlite_connection(database_url) as connection:
        snapshots = _load_portfolio_snapshots(connection, run_id)

    if not snapshots:
        return {"data": {"drawdown": []}, "meta": {}}

    values = [s.total_value for s in snapshots]
    dates = [s.date for s in snapshots]

    drawdowns = []
    peak = values[0]

    for date, value in zip(dates, values, strict=True):
        if value > peak:
            peak = value
        dd = (peak - value) / peak if peak > 0 else 0.0
        drawdowns.append((date, round(dd, 4)))

    return {
        "data": {"drawdown": drawdowns},
        "meta": {},
    }


def _load_portfolio_snapshots(
    connection,
    run_id: str,
) -> list[PortfolioSnapshot]:
    """加载组合快照。

    Args:
        connection: 数据库连接
        run_id: 回测运行 ID

    Returns:
        组合快照列表
    """
    from app.storage.schema import SNAPSHOTS_TABLE

    # 检查表是否存在
    table_check = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (SNAPSHOTS_TABLE,),
    ).fetchone()

    if table_check is None:
        return []

    rows = connection.execute(
        f"""
        select
            run_date,
            cash,
            total_value
        from {SNAPSHOTS_TABLE}
        where run_id = ?
        order by run_date
        """,
        (run_id,),
    ).fetchall()

    return [
        PortfolioSnapshot(
            date=row["run_date"],
            cash=row["cash"],
            positions=[],
            total_value=row["total_value"],
        )
        for row in rows
    ]
