from __future__ import annotations

import math
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class FactorIcResult:
    sample_size: int
    ic: float | None
    rank_ic: float | None


@dataclass(frozen=True)
class LayerReturnResult:
    layer: int
    stock_count: int
    average_factor_score: float
    average_forward_return: float


def calculate_forward_returns(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    holding_days: int,
) -> dict[str, float]:
    if holding_days <= 0:
        raise ValueError("holding_days must be greater than 0")

    target_date = (date.fromisoformat(score_date) + timedelta(days=holding_days)).isoformat()
    results: dict[str, float] = {}

    for stock_code in stock_codes:
        start_price = _get_price_on_or_before(connection, stock_code, score_date)
        end_price = _get_future_price_on_or_before(connection, stock_code, score_date, target_date)
        if start_price is None or end_price is None or start_price <= 0:
            continue
        results[stock_code] = (end_price / start_price) - 1

    return results


def calculate_information_coefficient(
    factor_scores: Mapping[str, float],
    forward_returns: Mapping[str, float],
) -> FactorIcResult:
    aligned = _align_values(factor_scores, forward_returns)
    if len(aligned) < 2:
        return FactorIcResult(sample_size=len(aligned), ic=None, rank_ic=None)

    score_values = [score for score, _ in aligned]
    return_values = [forward_return for _, forward_return in aligned]
    ic = _pearson_correlation(score_values, return_values)
    rank_ic = _pearson_correlation(
        _rank_values(score_values),
        _rank_values(return_values),
    )
    return FactorIcResult(sample_size=len(aligned), ic=ic, rank_ic=rank_ic)


def calculate_layer_returns(
    factor_scores: Mapping[str, float],
    forward_returns: Mapping[str, float],
    layers: int = 5,
) -> list[LayerReturnResult]:
    if layers <= 0:
        raise ValueError("layers must be greater than 0")

    aligned_items = [
        (stock_code, factor_scores[stock_code], forward_returns[stock_code])
        for stock_code in factor_scores
        if stock_code in forward_returns
        and _is_finite_number(factor_scores[stock_code])
        and _is_finite_number(forward_returns[stock_code])
    ]
    aligned_items.sort(key=lambda item: (-item[1], item[0]))
    if not aligned_items:
        return []

    actual_layers = min(layers, len(aligned_items))
    layer_size_base, remainder = divmod(len(aligned_items), actual_layers)
    results: list[LayerReturnResult] = []
    start = 0

    for index in range(actual_layers):
        size = layer_size_base + (1 if index < remainder else 0)
        items = aligned_items[start : start + size]
        start += size
        results.append(
            LayerReturnResult(
                layer=index + 1,
                stock_count=len(items),
                average_factor_score=sum(item[1] for item in items) / len(items),
                average_forward_return=sum(item[2] for item in items) / len(items),
            )
        )

    return results


def _get_price_on_or_before(
    connection: sqlite3.Connection,
    stock_code: str,
    target_date: str,
) -> float | None:
    row = connection.execute(
        """
        select close_price, adjusted_close
        from daily_prices
        where stock_code = ?
          and trade_date <= ?
          and is_suspended = 0
        order by trade_date desc
        limit 1
        """,
        (stock_code, target_date),
    ).fetchone()
    if row is None:
        return None
    return row["adjusted_close"] if row["adjusted_close"] is not None else row["close_price"]


def _get_future_price_on_or_before(
    connection: sqlite3.Connection,
    stock_code: str,
    score_date: str,
    target_date: str,
) -> float | None:
    row = connection.execute(
        """
        select close_price, adjusted_close
        from daily_prices
        where stock_code = ?
          and trade_date > ?
          and trade_date <= ?
          and is_suspended = 0
        order by trade_date desc
        limit 1
        """,
        (stock_code, score_date, target_date),
    ).fetchone()
    if row is None:
        return None
    return row["adjusted_close"] if row["adjusted_close"] is not None else row["close_price"]


def _align_values(
    factor_scores: Mapping[str, float],
    forward_returns: Mapping[str, float],
) -> list[tuple[float, float]]:
    return [
        (factor_scores[stock_code], forward_returns[stock_code])
        for stock_code in sorted(factor_scores)
        if stock_code in forward_returns
        and _is_finite_number(factor_scores[stock_code])
        and _is_finite_number(forward_returns[stock_code])
    ]


def _pearson_correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None

    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True))
    left_variance = sum((x - left_mean) ** 2 for x in left)
    right_variance = sum((y - right_mean) ** 2 for y in right)
    denominator = math.sqrt(left_variance * right_variance)
    if denominator == 0:
        return None
    return numerator / denominator


def _rank_values(values: list[float]) -> list[float]:
    indexed_values = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0

    while index < len(indexed_values):
        tie_end = index + 1
        while (
            tie_end < len(indexed_values) and indexed_values[tie_end][1] == indexed_values[index][1]
        ):
            tie_end += 1

        average_rank = (index + 1 + tie_end) / 2
        for original_index, _ in indexed_values[index:tie_end]:
            ranks[original_index] = average_rank
        index = tie_end

    return ranks


def _is_finite_number(value: float) -> bool:
    return isinstance(value, int | float) and math.isfinite(value)
