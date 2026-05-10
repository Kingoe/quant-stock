import pytest

from app.broker_evaluation import (
    BrokerReadinessCriteria,
    BrokerReadinessInput,
    evaluate_broker_readiness,
)


def test_evaluate_broker_readiness_blocks_when_simulation_is_too_short() -> None:
    result = evaluate_broker_readiness(
        BrokerReadinessInput(
            simulation_days=20,
            max_drawdown=0.08,
            failed_runs=0,
            notifications_enabled=True,
            manual_approval_enabled=True,
            paper_trading_verified=True,
        )
    )

    assert result.status == "blocked"
    assert result.ready_for_manual_pilot is False
    assert "模拟运行天数不足" in result.failed_reasons
    assert result.allowed_actions == ["read_account", "read_positions", "read_orders"]


def test_evaluate_broker_readiness_allows_manual_pilot_review_when_all_checks_pass() -> None:
    result = evaluate_broker_readiness(
        BrokerReadinessInput(
            simulation_days=90,
            max_drawdown=0.10,
            failed_runs=0,
            notifications_enabled=True,
            manual_approval_enabled=True,
            paper_trading_verified=True,
        )
    )

    assert result.status == "manual_pilot_review"
    assert result.ready_for_manual_pilot is True
    assert result.failed_reasons == []
    assert "place_order" not in result.allowed_actions


def test_evaluate_broker_readiness_reports_all_failed_reasons() -> None:
    result = evaluate_broker_readiness(
        BrokerReadinessInput(
            simulation_days=90,
            max_drawdown=0.30,
            failed_runs=2,
            notifications_enabled=False,
            manual_approval_enabled=False,
            paper_trading_verified=False,
        )
    )

    assert result.status == "blocked"
    assert result.failed_reasons == [
        "最大回撤超过阈值",
        "存在失败运行记录",
        "通知渠道未启用",
        "人工确认开关未启用",
        "模拟交易验证未完成",
    ]


def test_evaluate_broker_readiness_supports_custom_criteria() -> None:
    result = evaluate_broker_readiness(
        BrokerReadinessInput(
            simulation_days=45,
            max_drawdown=0.18,
            failed_runs=1,
            notifications_enabled=True,
            manual_approval_enabled=True,
            paper_trading_verified=True,
        ),
        BrokerReadinessCriteria(
            min_simulation_days=30,
            max_allowed_drawdown=0.20,
            max_failed_runs=1,
        ),
    )

    assert result.ready_for_manual_pilot is True


def test_evaluate_broker_readiness_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="simulation_days"):
        evaluate_broker_readiness(
            BrokerReadinessInput(
                simulation_days=-1,
                max_drawdown=0.10,
                failed_runs=0,
                notifications_enabled=True,
                manual_approval_enabled=True,
                paper_trading_verified=True,
            )
        )

    with pytest.raises(ValueError, match="max_drawdown"):
        evaluate_broker_readiness(
            BrokerReadinessInput(
                simulation_days=90,
                max_drawdown=-0.01,
                failed_runs=0,
                notifications_enabled=True,
                manual_approval_enabled=True,
                paper_trading_verified=True,
            )
        )
