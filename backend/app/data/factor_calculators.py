from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from app.data.factors import get_aligned_financial


def calculate_liquidity_factor(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    average_amount_weight: float = 1.0,
    lookback_days: int = 20,
) -> dict[str, float]:
    """计算流动性因子得分

    流动性因子包含：
    - 近 20 日平均成交额: 平均成交额越高越好

    历史成交额不足窗口期时，对应股票得到中性得分。
    """
    start_date = _subtract_days(score_date, lookback_days)
    average_amounts: dict[str, float | None] = {}
    for stock_code in stock_codes:
        amounts = _get_amounts_between(connection, stock_code, start_date, score_date)
        if len(amounts) < lookback_days:
            average_amounts[stock_code] = None
        else:
            average_amounts[stock_code] = sum(amounts[-lookback_days:]) / lookback_days

    if not average_amounts:
        return {}

    average_amount_scores = _rank_values(average_amounts, reverse=False)
    return {
        stock_code: average_amount_scores.get(stock_code, 0.5) * average_amount_weight
        for stock_code in average_amounts
    }


def calculate_risk_factor(
    connection: sqlite3.Connection,
    stock_codes: list[str],
    score_date: str,
    volatility_weight: float = 0.5,
    max_drawdown_weight: float = 0.5,
    lookback_days: int = 120,
) -> dict[str, float]:
    """计算风险因子得分

    风险因子包含：
    - 波动率: 日收益波动越低越好
    - 最大回撤: 回撤越低越好

    价格优先使用 adjusted_close，缺失时使用 close_price。
    """
    valid_stocks: dict[str, dict[str, float | None]] = {}
    start_date = _subtract_days(score_date, lookback_days)
    for stock_code in stock_codes:
        prices = _get_prices_between(connection, stock_code, start_date, score_date)
        if prices:
            valid_stocks[stock_code] = {
                "volatility": _calculate_volatility(prices),
                "max_drawdown": _calculate_max_drawdown(prices),
            }

    if not valid_stocks:
        return {}

    volatility_scores = _rank_values(
        {code: data["volatility"] for code, data in valid_stocks.items()},
        reverse=True,
    )
    max_drawdown_scores = _rank_non_negative_values(
        {code: data["max_drawdown"] for code, data in valid_stocks.items()},
        reverse=True,
    )

    scores: dict[str, float] = {}
    for stock_code in valid_stocks:
        scores[stock_code] = (
            volatility_scores.get(stock_code, 0.5) * volatility_weight
            + max_drawdown_scores.get(stock_code, 0.5) * max_drawdown_weight
        )

    return scores


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


def _get_prices_between(
    connection: sqlite3.Connection,
    stock_code: str,
    start_date: str,
    end_date: str,
) -> list[float]:
    rows = connection.execute(
        """
        select close_price, adjusted_close
        from daily_prices
        where stock_code = ?
          and trade_date >= ?
          and trade_date <= ?
        order by trade_date
        """,
        (stock_code, start_date, end_date),
    ).fetchall()
    prices: list[float] = []
    for row in rows:
        if row["adjusted_close"] is not None:
            prices.append(row["adjusted_close"])
        else:
            prices.append(row["close_price"])
    return prices


def _get_amounts_between(
    connection: sqlite3.Connection,
    stock_code: str,
    start_date: str,
    end_date: str,
) -> list[float]:
    rows = connection.execute(
        """
        select amount
        from daily_prices
        where stock_code = ?
          and trade_date >= ?
          and trade_date <= ?
        order by trade_date
        """,
        (stock_code, start_date, end_date),
    ).fetchall()
    return [row["amount"] for row in rows]


def _calculate_return(current_price: float, previous_price: float | None) -> float | None:
    if previous_price is None or previous_price <= 0:
        return None
    return current_price / previous_price - 1


def _calculate_volatility(prices: list[float]) -> float | None:
    returns = [
        _calculate_return(current_price, previous_price)
        for previous_price, current_price in zip(prices, prices[1:], strict=False)
    ]
    valid_returns = [value for value in returns if value is not None]
    if len(valid_returns) < 2:
        return None

    mean_return = sum(valid_returns) / len(valid_returns)
    variance = sum((value - mean_return) ** 2 for value in valid_returns) / len(valid_returns)
    return variance**0.5


def _calculate_max_drawdown(prices: list[float]) -> float | None:
    if len(prices) < 2:
        return None

    peak = prices[0]
    max_drawdown = 0.0
    for price in prices:
        if price > peak:
            peak = price
        if peak <= 0:
            continue
        drawdown = 1 - price / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    return max_drawdown


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
    return rank_factor_values(
        values,
        higher_is_better=not reverse,
        allow_zero=False,
        winsorize=False,
    )


def _rank_non_negative_values(
    values: Mapping[str, float | None], reverse: bool
) -> dict[str, float]:
    """将非负值转换为排名得分，适用于最大回撤等 0 也有效的指标。"""
    return rank_factor_values(
        values,
        higher_is_better=not reverse,
        allow_zero=True,
        winsorize=False,
    )


def rank_factor_values(
    values: Mapping[str, float | None],
    *,
    higher_is_better: bool,
    allow_zero: bool = False,
    winsorize: bool = True,
    lower_quantile: float = 0.05,
    upper_quantile: float = 0.95,
) -> dict[str, float]:
    """将因子原始值转换为 0-1 排名得分。"""
    valid_items = [
        (code, value)
        for code, value in values.items()
        if value is not None and (value >= 0 if allow_zero else value > 0)
    ]

    if len(valid_items) < 2:
        return {code: 0.5 for code in values}

    rank_values: Mapping[str, float | None]
    if winsorize:
        rank_values = winsorize_factor_values(
            dict(valid_items),
            lower_quantile=lower_quantile,
            upper_quantile=upper_quantile,
        )
    else:
        rank_values = dict(valid_items)

    sorted_items = sorted(
        rank_values.items(),
        key=lambda item: item[1] if item[1] is not None else 0.0,
        reverse=not higher_is_better,
    )
    count = len(sorted_items)

    scores: dict[str, float] = {}
    index = 0
    while index < count:
        _, value = sorted_items[index]
        next_index = index + 1
        while next_index < count and sorted_items[next_index][1] == value:
            next_index += 1

        rank_score = ((index + next_index - 1) / 2) / (count - 1)
        for item_index in range(index, next_index):
            code, _ = sorted_items[item_index]
            scores[code] = rank_score

        index = next_index

    for code in values:
        if code not in scores:
            scores[code] = 0.5

    return scores


def winsorize_factor_values(
    values: Mapping[str, float | None],
    *,
    lower_quantile: float = 0.05,
    upper_quantile: float = 0.95,
) -> dict[str, float | None]:
    """按分位数对因子值做去极值处理。"""
    if lower_quantile < 0 or upper_quantile > 1 or lower_quantile > upper_quantile:
        raise ValueError("quantiles must satisfy 0 <= lower <= upper <= 1")

    valid_items = [(code, value) for code, value in values.items() if value is not None]

    if len(valid_items) < 2:
        return dict(values)

    sorted_values = sorted(value for _, value in valid_items)
    lower_bound = _quantile(sorted_values, lower_quantile)
    upper_bound = _quantile(sorted_values, upper_quantile)

    winsorized: dict[str, float | None] = {}
    for code in values:
        value = values[code]
        if value is None:
            winsorized[code] = None
        else:
            winsorized[code] = min(max(value, lower_bound), upper_bound)

    return winsorized


def _quantile(sorted_values: list[float], quantile: float) -> float:
    position = (len(sorted_values) - 1) * quantile
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = position - lower_index
    return (
        sorted_values[lower_index]
        + (sorted_values[upper_index] - sorted_values[lower_index]) * fraction
    )
