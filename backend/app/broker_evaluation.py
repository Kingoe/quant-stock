from __future__ import annotations

from dataclasses import dataclass

READ_ONLY_BROKER_ACTIONS = ["read_account", "read_positions", "read_orders"]


@dataclass(frozen=True)
class BrokerReadinessCriteria:
    min_simulation_days: int = 60
    max_allowed_drawdown: float = 0.15
    max_failed_runs: int = 0
    require_notifications: bool = True
    require_manual_approval: bool = True
    require_paper_trading_verified: bool = True


@dataclass(frozen=True)
class BrokerReadinessInput:
    simulation_days: int
    max_drawdown: float
    failed_runs: int
    notifications_enabled: bool
    manual_approval_enabled: bool
    paper_trading_verified: bool


@dataclass(frozen=True)
class BrokerReadinessResult:
    status: str
    ready_for_manual_pilot: bool
    failed_reasons: list[str]
    allowed_actions: list[str]


def evaluate_broker_readiness(
    readiness: BrokerReadinessInput,
    criteria: BrokerReadinessCriteria | None = None,
) -> BrokerReadinessResult:
    active_criteria = criteria or BrokerReadinessCriteria()
    _validate_readiness(readiness)
    _validate_criteria(active_criteria)

    failed_reasons: list[str] = []
    if readiness.simulation_days < active_criteria.min_simulation_days:
        failed_reasons.append("模拟运行天数不足")
    if readiness.max_drawdown > active_criteria.max_allowed_drawdown:
        failed_reasons.append("最大回撤超过阈值")
    if readiness.failed_runs > active_criteria.max_failed_runs:
        failed_reasons.append("存在失败运行记录")
    if active_criteria.require_notifications and not readiness.notifications_enabled:
        failed_reasons.append("通知渠道未启用")
    if active_criteria.require_manual_approval and not readiness.manual_approval_enabled:
        failed_reasons.append("人工确认开关未启用")
    if active_criteria.require_paper_trading_verified and not readiness.paper_trading_verified:
        failed_reasons.append("模拟交易验证未完成")

    ready = len(failed_reasons) == 0
    return BrokerReadinessResult(
        status="manual_pilot_review" if ready else "blocked",
        ready_for_manual_pilot=ready,
        failed_reasons=failed_reasons,
        allowed_actions=list(READ_ONLY_BROKER_ACTIONS),
    )


def _validate_readiness(readiness: BrokerReadinessInput) -> None:
    if readiness.simulation_days < 0:
        raise ValueError("simulation_days must be greater than or equal to 0")
    if readiness.max_drawdown < 0:
        raise ValueError("max_drawdown must be greater than or equal to 0")
    if readiness.failed_runs < 0:
        raise ValueError("failed_runs must be greater than or equal to 0")


def _validate_criteria(criteria: BrokerReadinessCriteria) -> None:
    if criteria.min_simulation_days <= 0:
        raise ValueError("min_simulation_days must be greater than 0")
    if criteria.max_allowed_drawdown < 0:
        raise ValueError("max_allowed_drawdown must be greater than or equal to 0")
    if criteria.max_failed_runs < 0:
        raise ValueError("max_failed_runs must be greater than or equal to 0")
