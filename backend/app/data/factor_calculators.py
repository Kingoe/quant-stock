from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from app.data.factors import get_aligned_valuation


def calculate_valuation_factor(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    pe_weight: float = 0.5,
    pb_weight: float = 0.3,
    dividend_yield_weight: float = 0.2,
) -> dict[str, float]:
    """计算估值因子得分

    估值因子包含：
    - PE: PE 越低越好（需要倒序排名）
    - PB: PB 越低越好（需要倒序排名）
    - 股息率: 越高越好（正常排名）

    权重和为 1.0，可根据需要调整。
    """
    # 收集有效估值数据
    valid_stocks: dict[str, dict[str, float | None]] = {}
    for stock_code in stock_codes:
        valuation = get_aligned_valuation(connection, stock_code, score_date)
        if valuation:
            valid_stocks[stock_code] = {
                "pe": valuation["pe"],
                "pb": valuation["pb"],
                "dividend_yield": valuation["dividend_yield"],
            }

    if not valid_stocks:
        return {}

    # 计算各子因子的排名得分
    pe_scores = _rank_values(
        {code: data["pe"] for code, data in valid_stocks.items()}, reverse=True
    )
    pb_scores = _rank_values(
        {code: data["pb"] for code, data in valid_stocks.items()}, reverse=True
    )
    dividend_scores = _rank_values(
        {code: data["dividend_yield"] for code, data in valid_stocks.items()}, reverse=False
    )

    # 计算加权得分
    scores: dict[str, float] = {}
    for stock_code in valid_stocks:
        scores[stock_code] = (
            pe_scores.get(stock_code, 0.5) * pe_weight
            + pb_scores.get(stock_code, 0.5) * pb_weight
            + dividend_scores.get(stock_code, 0.5) * dividend_yield_weight
        )

    return scores


def _rank_values(
    values: Mapping[str, float | None], reverse: bool
) -> dict[str, float]:
    """将值转换为排名得分 (0-1)

    Args:
        values: 股票代码到值的映射
        reverse: 是否倒序（True 表示值越小得分越高）

    Returns:
        股票代码到归一化得分的映射 (0-1)
    """
    # 过滤空值和负值
    valid_items = [(code, v) for code, v in values.items() if v is not None and v > 0]

    if len(valid_items) < 2:
        # 如果有效值少于 2 个，所有股票返回 0.5
        return {code: 0.5 for code in values}

    # 按值排序
    sorted_items = sorted(valid_items, key=lambda x: x[1], reverse=reverse)
    count = len(sorted_items)

    # 计算排名得分
    scores: dict[str, float] = {}
    for idx, (code, _) in enumerate(sorted_items):
        # 归一化到 0-1 范围
        scores[code] = idx / (count - 1)

    # 未包含的股票返回 0.5
    for code in values:
        if code not in scores:
            scores[code] = 0.5

    return scores