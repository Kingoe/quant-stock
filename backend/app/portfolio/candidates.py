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
