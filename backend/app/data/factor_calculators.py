from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from app.data.factors import get_aligned_financial


def calculate_momentum_factor(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    momentum_60_weight: float = 0.5,
    momentum_120_weight: float = 0.5,
) -> dict[str, float]:
    """计算动量因子得分

    动量因子包含：
    - 60 日涨跌幅: 近 60 日涨幅越高越好
    - 120 日涨跌幅: 近 120 日涨幅越高越好

    价格优先使用 adjusted_close，缺失时使用 close_price。
    """
    valid_stocks: dict[str, dict[str, float | None]] = {}
    for stock_code in stock_codes:
        current_price = _get_price_on_or_before(connection, stock_code, score_date)
        price_60 = _get_price_on_or_before(
            connection,
            stock_code,
            _subtract_days(score_date, 60),
        )
        price_120 = _get_price_on_or_before(
            connection,
            stock_code,
            _subtract_days(score_date, 120),
        )
        if current_price is not None:
            valid_stocks[stock_code] = {
                "momentum_60": _calculate_return(current_price, price_60),
                "momentum_120": _calculate_return(current_price, price_120),
            }

    if not valid_stocks:
        return {}

    momentum_60_scores = _rank_values(
        {code: data["momentum_60"] for code, data in valid_stocks.items()},
        reverse=False,
    )
    momentum_120_scores = _rank_values(
        {code: data["momentum_120"] for code, data in valid_stocks.items()},
        reverse=False,
    )

    scores: dict[str, float] = {}
    for stock_code in valid_stocks:
        scores[stock_code] = (
            momentum_60_scores.get(stock_code, 0.5) * momentum_60_weight
            + momentum_120_scores.get(stock_code, 0.5) * momentum_120_weight
        )

    return scores


def calculate_growth_factor(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    revenue_growth_weight: float = 0.5,
    net_profit_growth_weight: float = 0.5,
) -> dict[str, float]:
    """计算成长因子得分

    成长因子包含：
    - 营收增速: 营收增速越高越好（正常排名）
    - 净利润增速: 净利润增速越高越好（正常排名）

    权重和默认为 1.0，可根据需要调整。
    """
    valid_stocks: dict[str, dict[str, float | None]] = {}
    for stock_code in stock_codes:
        financial = get_aligned_financial(connection, stock_code, score_date)
        if financial:
            valid_stocks[stock_code] = {
                "revenue_growth": financial["revenue_growth"],
                "net_profit_growth": financial["net_profit_growth"],
            }

    if not valid_stocks:
        return {}

    revenue_growth_scores = _rank_values(
        {code: data["revenue_growth"] for code, data in valid_stocks.items()},
        reverse=False,
    )
    net_profit_growth_scores = _rank_values(
        {code: data["net_profit_growth"] for code, data in valid_stocks.items()},
        reverse=False,
    )

    scores: dict[str, float] = {}
    for stock_code in valid_stocks:
        scores[stock_code] = (
            revenue_growth_scores.get(stock_code, 0.5) * revenue_growth_weight
            + net_profit_growth_scores.get(stock_code, 0.5) * net_profit_growth_weight
        )

    return scores


def calculate_quality_factor(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    roe_weight: float = 0.4,
    gross_margin_weight: float = 0.3,
    cash_flow_weight: float = 0.3,
) -> dict[str, float]:
    """计算质量因子得分

    质量因子包含：
    - ROE: ROE 越高越好（正常排名）
    - 毛利率: 毛利率越高质量得分越好（正常排名）
    - 现金流质量: 经营现金流 / 净利润 越高质量得分越好（正常排名）

    权重和为 1.0，可根据需要调整。
    """
    # 收集有效财务数据
    valid_stocks: dict[str, dict[str, float | None]] = {}
    for stock_code in stock_codes:
        financial = get_aligned_financial(connection, stock_code, score_date)
        if financial:
            valid_stocks[stock_code] = {
                "roe": financial["roe"],
                "gross_margin": financial["gross_margin"],
                "cash_flow_quality": _calculate_cash_flow_quality(financial),
            }

    if not valid_stocks:
        return {}

    # 计算各子因子的排名得分
    roe_scores = _rank_values(
        {code: data["roe"] for code, data in valid_stocks.items()}, reverse=False
    )
    gross_margin_scores = _rank_values(
        {code: data["gross_margin"] for code, data in valid_stocks.items()}, reverse=False
    )
    cash_flow_scores = _rank_values(
        {code: data["cash_flow_quality"] for code, data in valid_stocks.items()},
        reverse=False,
    )

    # 计算加权得分
    scores: dict[str, float] = {}
    for stock_code in valid_stocks:
        scores[stock_code] = (
            roe_scores.get(stock_code, 0.5) * roe_weight
            + gross_margin_scores.get(stock_code, 0.5) * gross_margin_weight
            + cash_flow_scores.get(stock_code, 0.5) * cash_flow_weight
        )

    return scores


def _calculate_cash_flow_quality(financial: sqlite3.Row) -> float | None:
    """计算现金流质量：经营现金流 / 净利润"""
    if (
        financial["operating_cash_flow"] is None
        or financial["net_profit"] is None
        or financial["net_profit"] == 0
    ):
        return None
    return financial["operating_cash_flow"] / financial["net_profit"]


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
        order by trade_date desc
        limit 1
        """,
        (stock_code, target_date),
    ).fetchone()
    if row is None:
        return None
    if row["adjusted_close"] is not None:
        return row["adjusted_close"]
    return row["close_price"]


def _calculate_return(current_price: float, previous_price: float | None) -> float | None:
    if previous_price is None or previous_price <= 0:
        return None
    return current_price / previous_price - 1


def _subtract_days(value: str, days: int) -> str:
    return (date.fromisoformat(value) - timedelta(days=days)).isoformat()


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
    from app.data.factors import get_aligned_valuation

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
        {code: data["dividend_yield"] for code, data in valid_stocks.items()},
        reverse=False,
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


def _rank_values(values: Mapping[str, float | None], reverse: bool) -> dict[str, float]:
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
