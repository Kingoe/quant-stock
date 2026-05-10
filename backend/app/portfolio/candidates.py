from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass

from app.data import calculate_total_factor_scores


@dataclass(frozen=True)
class CandidateStock:
    stock_code: str
    total_score: float
    rank: int


@dataclass(frozen=True)
class TargetPosition:
    stock_code: str
    total_score: float
    rank: int
    target_weight: float


@dataclass(frozen=True)
class RebalanceRecommendation:
    stock_code: str
    stock_name: str | None
    action: str
    target_weight: float | None
    total_score: float
    rank: int | None
    reason: str
    risk_note: str | None


@dataclass(frozen=True)
class TradingStatus:
    is_limit_up: bool = False
    is_limit_down: bool = False
    is_suspended: bool = False


def select_top_candidates(
    stock_codes: list[str],
    total_scores: Mapping[str, float],
    *,
    limit: int,
) -> list[CandidateStock]:
    """按总分选择排名靠前的候选股。"""
    if limit <= 0:
        raise ValueError("limit must be positive")

    ranked_items = sorted(
        (
            (stock_code, total_scores[stock_code])
            for stock_code in stock_codes
            if stock_code in total_scores
        ),
        key=lambda item: (-item[1], item[0]),
    )

    return [
        CandidateStock(stock_code=stock_code, total_score=total_score, rank=index + 1)
        for index, (stock_code, total_score) in enumerate(ranked_items[:limit])
    ]


def calculate_top_candidates(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    *,
    limit: int,
) -> list[CandidateStock]:
    total_scores = calculate_total_factor_scores(connection, stock_codes, score_date)
    return select_top_candidates(stock_codes, total_scores, limit=limit)


def apply_single_stock_weight_limit(
    candidates: list[CandidateStock],
    *,
    single_stock_max_weight: float,
) -> list[TargetPosition]:
    if single_stock_max_weight <= 0:
        raise ValueError("single_stock_max_weight must be greater than 0")
    if single_stock_max_weight > 1:
        raise ValueError("single_stock_max_weight must be less than or equal to 1")
    if not candidates:
        return []

    equal_weight = 1 / len(candidates)
    target_weight = min(equal_weight, single_stock_max_weight)

    return [
        TargetPosition(
            stock_code=candidate.stock_code,
            total_score=candidate.total_score,
            rank=candidate.rank,
            target_weight=target_weight,
        )
        for candidate in candidates
    ]


def calculate_target_positions(
    stock_codes: list[str],
    total_scores: Mapping[str, float],
    *,
    limit: int,
    single_stock_max_weight: float,
) -> list[TargetPosition]:
    candidates = select_top_candidates(stock_codes, total_scores, limit=limit)
    return apply_single_stock_weight_limit(
        candidates,
        single_stock_max_weight=single_stock_max_weight,
    )


def apply_industry_weight_limit(
    positions: list[TargetPosition],
    industries: Mapping[str, str | None],
    *,
    industry_max_weight: float,
) -> list[TargetPosition]:
    if industry_max_weight <= 0:
        raise ValueError("industry_max_weight must be greater than 0")
    if industry_max_weight > 1:
        raise ValueError("industry_max_weight must be less than or equal to 1")

    used_by_industry: dict[str, float] = {}
    capped_positions: list[TargetPosition] = []
    for position in positions:
        industry = industries.get(position.stock_code) or "未知"
        used_weight = used_by_industry.get(industry, 0.0)
        remaining_weight = max(industry_max_weight - used_weight, 0.0)
        target_weight = min(position.target_weight, remaining_weight)
        used_by_industry[industry] = used_weight + target_weight
        capped_positions.append(
            TargetPosition(
                stock_code=position.stock_code,
                total_score=position.total_score,
                rank=position.rank,
                target_weight=target_weight,
            )
        )

    return capped_positions


def generate_rebalance_recommendations(
    target_positions: list[TargetPosition],
    current_positions: Mapping[str, float] | None,
    stock_names: Mapping[str, str | None],
    total_scores: Mapping[str, float] | None,
    top_candidates: list[CandidateStock] | None,
) -> list[RebalanceRecommendation]:
    """生成买入、卖出、持有、观察列表。

    Args:
        target_positions: 目标持仓列表
        current_positions: 当前持仓股票代码到权重的映射，None 表示无持仓
        stock_names: 股票代码到名称的映射
        total_scores: 股票代码到总分的映射
        top_candidates: 优选候选股列表，用于生成观察列表

    Returns:
        调仓建议列表，按 action 排序：buy、hold、sell、watch
    """
    if current_positions is None:
        current_positions = {}
    if total_scores is None:
        total_scores = {}
    if top_candidates is None:
        top_candidates = []

    target_stock_set = {p.stock_code for p in target_positions}
    current_stock_set = set(current_positions.keys())

    recommendations: list[RebalanceRecommendation] = []

    target_stock_map = {p.stock_code: p for p in target_positions}

    for stock_code in target_stock_set - current_stock_set:
        position = target_stock_map[stock_code]
        recommendations.append(
            RebalanceRecommendation(
                stock_code=stock_code,
                stock_name=stock_names.get(stock_code),
                action="buy",
                target_weight=position.target_weight,
                total_score=total_scores.get(stock_code, 0.0),
                rank=position.rank,
                reason="新增目标持仓",
                risk_note=None,
            )
        )

    for stock_code in current_stock_set - target_stock_set:
        recommendations.append(
            RebalanceRecommendation(
                stock_code=stock_code,
                stock_name=stock_names.get(stock_code),
                action="sell",
                target_weight=None,
                total_score=total_scores.get(stock_code, 0.0),
                rank=None,
                reason="已不在目标组合中",
                risk_note=None,
            )
        )

    for stock_code in target_stock_set & current_stock_set:
        position = target_stock_map[stock_code]
        recommendations.append(
            RebalanceRecommendation(
                stock_code=stock_code,
                stock_name=stock_names.get(stock_code),
                action="hold",
                target_weight=position.target_weight,
                total_score=total_scores.get(stock_code, 0.0),
                rank=position.rank,
                reason="继续持有",
                risk_note=None,
            )
        )

    for candidate in top_candidates:
        if candidate.stock_code not in target_stock_set:
            recommendations.append(
                RebalanceRecommendation(
                    stock_code=candidate.stock_code,
                    stock_name=stock_names.get(candidate.stock_code),
                    action="watch",
                    target_weight=None,
                    total_score=candidate.total_score,
                    rank=candidate.rank,
                    reason="高分观察股",
                    risk_note=None,
                )
            )

    action_order = {"buy": 0, "hold": 1, "sell": 2, "watch": 3}
    recommendations.sort(key=lambda r: (action_order.get(r.action, 99), r.stock_code))

    return recommendations


def add_trading_availability_notes(
    recommendations: list[RebalanceRecommendation],
    trading_status: Mapping[str, TradingStatus],
) -> list[RebalanceRecommendation]:
    """为调仓建议添加交易可用性风险提示。

    Args:
        recommendations: 调仓建议列表
        trading_status: 股票代码到交易状态的映射

    Returns:
        添加风险提示后的调仓建议列表

    风险提示规则：
    - 买入 + 涨停 → "涨停无法买入"
    - 卖出 + 跌停 → "跌停无法卖出"
    - 买入/卖出 + 停牌 → "停牌无法交易"
    """
    updated: list[RebalanceRecommendation] = []
    for recommendation in recommendations:
        status = trading_status.get(recommendation.stock_code)
        risk_note = None

        if status and status.is_suspended:
            if recommendation.action in ("buy", "sell"):
                risk_note = "停牌无法交易"
        elif status and status.is_limit_up:
            if recommendation.action == "buy":
                risk_note = "涨停无法买入"
        elif status and status.is_limit_down:
            if recommendation.action == "sell":
                risk_note = "跌停无法卖出"

        if risk_note and recommendation.risk_note:
            risk_note = f"{recommendation.risk_note}；{risk_note}"

        updated.append(
            RebalanceRecommendation(
                stock_code=recommendation.stock_code,
                stock_name=recommendation.stock_name,
                action=recommendation.action,
                target_weight=recommendation.target_weight,
                total_score=recommendation.total_score,
                rank=recommendation.rank,
                reason=recommendation.reason,
                risk_note=risk_note or recommendation.risk_note,
            )
        )

    return updated
