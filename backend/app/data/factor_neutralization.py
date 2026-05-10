from __future__ import annotations

import math
from collections.abc import Mapping


def neutralize_scores_by_industry(
    scores: Mapping[str, float],
    industries: Mapping[str, str | None],
    *,
    min_industry_size: int = 2,
    neutral_score: float = 0.5,
) -> dict[str, float]:
    """按行业内排名中性化股票得分。

    中性化后，不同行业之间不直接比较原始分数，只比较同一行业内的相对强弱。
    """
    if min_industry_size <= 0:
        raise ValueError("min_industry_size must be greater than 0")

    grouped_scores: dict[str, list[tuple[str, float]]] = {}
    for stock_code, score in scores.items():
        if not isinstance(score, int | float) or not math.isfinite(score):
            continue
        industry = industries.get(stock_code) or "未知"
        grouped_scores.setdefault(industry, []).append((stock_code, float(score)))

    neutralized: dict[str, float] = {}
    for industry_scores in grouped_scores.values():
        if len(industry_scores) < min_industry_size:
            for stock_code, _ in industry_scores:
                neutralized[stock_code] = neutral_score
            continue

        ranked_values = _rank_scores_ascending(industry_scores)
        max_rank = len(industry_scores) - 1
        for stock_code, rank in ranked_values.items():
            neutralized[stock_code] = rank / max_rank if max_rank > 0 else neutral_score

    return neutralized


def _rank_scores_ascending(items: list[tuple[str, float]]) -> dict[str, float]:
    ranked_items = sorted(items, key=lambda item: (item[1], item[0]))
    ranks: dict[str, float] = {}
    index = 0

    while index < len(ranked_items):
        tie_end = index + 1
        while tie_end < len(ranked_items) and ranked_items[tie_end][1] == ranked_items[index][1]:
            tie_end += 1

        average_rank = (index + tie_end - 1) / 2
        for stock_code, _ in ranked_items[index:tie_end]:
            ranks[stock_code] = average_rank
        index = tie_end

    return ranks
