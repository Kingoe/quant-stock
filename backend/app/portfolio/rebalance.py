from __future__ import annotations

import sqlite3
from collections.abc import Mapping

from app.data import (
    calculate_total_factor_scores,
    filter_stocks,
    get_prices_by_trade_date,
    get_stock,
    get_universe_stock_codes,
)
from app.portfolio import (
    RebalanceRecommendation,
    TradingStatus,
    add_trading_availability_notes,
    apply_industry_weight_limit,
    calculate_target_positions,
    generate_rebalance_recommendations,
    select_top_candidates,
)


def generate_weekly_rebalance(
    connection: sqlite3.Connection,
    index_code: str,
    score_date: str,
    *,
    limit: int = 15,
    single_stock_max_weight: float = 0.08,
    industry_max_weight: float = 0.3,
    current_positions: Mapping[str, float] | None = None,
) -> list[RebalanceRecommendation]:
    """生成周频调仓建议。

    Args:
        connection: SQLite 连接
        index_code: 指数代码，如 "000906"（中证 800）
        score_date: 评分日期
        limit: 候选股数量上限
        single_stock_max_weight: 单票最大仓位
        industry_max_weight: 单个行业最大仓位
        current_positions: 当前持仓，None 表示无持仓

    Returns:
        调仓建议列表
    """
    if current_positions is None:
        current_positions = {}

    stock_codes = get_universe_stock_codes(connection, index_code, score_date)
    if not stock_codes:
        return []

    stock_codes = filter_stocks(connection, stock_codes)

    total_scores = calculate_total_factor_scores(connection, stock_codes, score_date)
    if not total_scores:
        return []

    candidates = select_top_candidates(stock_codes, total_scores, limit=limit)
    if not candidates:
        return []

    target_positions = calculate_target_positions(
        stock_codes,
        total_scores,
        limit=limit,
        single_stock_max_weight=single_stock_max_weight,
    )

    stock_names = {code: get_stock(connection, code)["stock_name"] for code in stock_codes}
    industries = {code: get_stock(connection, code)["industry"] for code in stock_codes}

    target_positions = apply_industry_weight_limit(
        target_positions,
        industries,
        industry_max_weight=industry_max_weight,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions,
        current_positions,
        stock_names,
        total_scores,
        candidates,
    )

    price_rows = {
        row["stock_code"]: row for row in get_prices_by_trade_date(connection, score_date)
    }
    trading_status: dict[str, TradingStatus] = {}
    for stock_code in [r.stock_code for r in recommendations]:
        price_row = price_rows.get(stock_code)
        if price_row:
            trading_status[stock_code] = TradingStatus(
                is_limit_up=bool(price_row["is_limit_up"]),
                is_limit_down=bool(price_row["is_limit_down"]),
                is_suspended=bool(price_row["is_suspended"]),
            )

    recommendations = add_trading_availability_notes(recommendations, trading_status)

    return recommendations
