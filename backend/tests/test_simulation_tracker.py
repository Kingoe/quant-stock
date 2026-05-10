from __future__ import annotations

from app.portfolio import RebalanceRecommendation


def test_create_signals() -> None:
    """测试创建策略信号记录。"""
    from app.simulation import create_signals
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        recommendations = [
            RebalanceRecommendation(
                stock_code="000001",
                stock_name="平安银行",
                action="buy",
                target_weight=0.08,
                total_score=0.75,
                rank=1,
                reason="新增目标持仓",
                risk_note=None,
            ),
            RebalanceRecommendation(
                stock_code="000002",
                stock_name="万科A",
                action="sell",
                target_weight=None,
                total_score=0.60,
                rank=None,
                reason="已不在目标组合中",
                risk_note="涨停无法卖出",
            ),
        ]

        signals = create_signals(connection, recommendations, "2026-05-10")

        assert len(signals) == 2
        assert signals[0].stock_code == "000001"
        assert signals[0].action == "buy"
        assert signals[0].executed is False
        assert signals[1].stock_code == "000002"
        assert signals[1].action == "sell"
        assert signals[1].risk_note == "涨停无法卖出"


def test_record_execution() -> None:
    """测试记录信号执行。"""
    from app.simulation import record_execution
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        # 先创建信号
        from app.portfolio import RebalanceRecommendation
        from app.simulation import create_signals

        recommendations = [
            RebalanceRecommendation(
                stock_code="000001",
                stock_name="平安银行",
                action="buy",
                target_weight=0.08,
                total_score=0.75,
                rank=1,
                reason="新增目标持仓",
                risk_note=None,
            ),
        ]
        signals = create_signals(connection, recommendations, "2026-05-10")

        execution = record_execution(
            connection,
            signal_id=signals[0].id,
            stock_code="000001",
            action="buy",
            quantity=100,
            price=10.50,
            status="filled",
        )

        assert execution.id is not None
        assert execution.stock_code == "000001"
        assert execution.quantity == 100
        assert execution.price == 10.50
        assert execution.status == "filled"

        # 检查信号状态已更新
        signal = connection.execute(
            "select * from strategy_signals where id = ?",
            (signals[0].id,),
        ).fetchone()
        assert signal["executed"] == 1


def test_get_pending_signals() -> None:
    """测试获取待执行信号。"""
    from app.simulation import create_signals, get_pending_signals
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        recommendations = [
            RebalanceRecommendation(
                stock_code="000001",
                stock_name="平安银行",
                action="buy",
                target_weight=0.08,
                total_score=0.75,
                rank=1,
                reason="新增目标持仓",
                risk_note=None,
            ),
        ]

        create_signals(connection, recommendations, "2026-05-10")

        pending = get_pending_signals(connection, limit=10)

        assert len(pending) == 1
        assert pending[0].stock_code == "000001"
        assert pending[0].executed is False


def test_get_pending_signals_after_execution() -> None:
    """测试执行后不返回待执行信号。"""
    from app.simulation import create_signals, get_pending_signals, record_execution
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        recommendations = [
            RebalanceRecommendation(
                stock_code="000001",
                stock_name="平安银行",
                action="buy",
                target_weight=0.08,
                total_score=0.75,
                rank=1,
                reason="新增目标持仓",
                risk_note=None,
            ),
        ]

        signals = create_signals(connection, recommendations, "2026-05-10")
        record_execution(
            connection,
            signal_id=signals[0].id,
            stock_code="000001",
            action="buy",
            quantity=100,
            price=10.50,
            status="filled",
        )

        pending = get_pending_signals(connection, limit=10)

        assert len(pending) == 0


def test_get_execution_summary() -> None:
    """测试获取执行摘要。"""
    from app.simulation import create_signals, get_execution_summary, record_execution
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        recommendations = [
            RebalanceRecommendation(
                stock_code="000001",
                stock_name="平安银行",
                action="buy",
                target_weight=0.08,
                total_score=0.75,
                rank=1,
                reason="新增目标持仓",
                risk_note=None,
            ),
            RebalanceRecommendation(
                stock_code="000002",
                stock_name="万科A",
                action="buy",
                target_weight=0.08,
                total_score=0.70,
                rank=2,
                reason="新增目标持仓",
                risk_note=None,
            ),
        ]

        signals = create_signals(connection, recommendations, "2026-05-10")

        # 执行第一个信号
        record_execution(
            connection,
            signal_id=signals[0].id,
            stock_code="000001",
            action="buy",
            quantity=100,
            price=10.50,
            status="filled",
        )

        # 执行第二个信号但失败
        record_execution(
            connection,
            signal_id=signals[1].id,
            stock_code="000002",
            action="buy",
            quantity=100,
            price=8.50,
            status="failed",
            reason="资金不足",
        )

        summary = get_execution_summary(connection, run_date="2026-05-10")

        assert summary["total_signals"] == 2
        assert summary["executed_signals"] == 1
        assert summary["failed_signals"] == 1
        assert summary["pending_signals"] == 0
        assert summary["execution_rate"] == 0.5


def test_get_execution_summary_all_dates() -> None:
    """测试获取全部日期的执行摘要。"""
    from app.simulation import get_execution_summary
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        summary = get_execution_summary(connection)

        assert summary["total_signals"] == 0
        assert summary["executed_signals"] == 0
        assert summary["failed_signals"] == 0
        assert summary["pending_signals"] == 0
