from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class DataQualityIssue:
    """数据质量问题。"""

    level: str
    code: str
    message: str
    details: dict[str, Any]


@dataclass(frozen=True)
class DataQualityReport:
    """数据质量检查报告。"""

    status: str
    score_date: str
    summary: dict[str, int]
    issues: list[DataQualityIssue]


def generate_data_quality_report(
    connection: sqlite3.Connection,
    score_date: str,
) -> DataQualityReport:
    """生成指定评分日的数据质量报告。"""
    _parse_date(score_date)
    issues: list[DataQualityIssue] = []

    _check_stock_basics(connection, issues)
    _check_daily_prices(connection, score_date, issues)
    _check_valuations(connection, score_date, issues)
    _check_financial_metrics(connection, score_date, issues)

    summary = {
        "error": sum(1 for issue in issues if issue.level == "error"),
        "warning": sum(1 for issue in issues if issue.level == "warning"),
        "info": sum(1 for issue in issues if issue.level == "info"),
    }
    if summary["error"]:
        status = "error"
    elif summary["warning"]:
        status = "warning"
    else:
        status = "ok"

    return DataQualityReport(
        status=status,
        score_date=score_date,
        summary=summary,
        issues=issues,
    )


def _check_stock_basics(connection: sqlite3.Connection, issues: list[DataQualityIssue]) -> None:
    count = _count(connection, "select count(*) as count from stocks where status = 'active'")
    if count == 0:
        issues.append(
            DataQualityIssue(
                level="error",
                code="missing_stock_basics",
                message="缺少股票基础信息，无法确认股票名称、行业和状态。",
                details={"rows_count": 0},
            )
        )


def _check_daily_prices(
    connection: sqlite3.Connection,
    score_date: str,
    issues: list[DataQualityIssue],
) -> None:
    latest_date = _latest_date(connection, "daily_prices", "trade_date")
    if latest_date is None:
        issues.append(
            DataQualityIssue(
                level="error",
                code="missing_daily_prices",
                message="缺少日行情数据，无法计算动量、风险和流动性因子。",
                details={"required_date": score_date, "latest_date": None},
            )
        )
        return

    if latest_date < score_date:
        issues.append(
            DataQualityIssue(
                level="error",
                code="stale_daily_prices",
                message="日行情数据早于评分日，不能用于本次策略运行。",
                details={"required_date": score_date, "latest_date": latest_date},
            )
        )

    abnormal_count = _count(
        connection,
        """
        select count(*) as count
        from daily_prices
        where trade_date = ?
          and (close_price <= 0 or amount <= 0 or volume < 0)
        """,
        (latest_date,),
    )
    if abnormal_count:
        issues.append(
            DataQualityIssue(
                level="warning",
                code="abnormal_daily_price_fields",
                message="部分日行情字段异常，需要检查成交额、成交量或收盘价。",
                details={"trade_date": latest_date, "rows_count": abnormal_count},
            )
        )


def _check_valuations(
    connection: sqlite3.Connection,
    score_date: str,
    issues: list[DataQualityIssue],
) -> None:
    latest_date = _latest_date(connection, "valuation_metrics", "trade_date")
    if latest_date is None:
        issues.append(
            DataQualityIssue(
                level="error",
                code="missing_valuation_metrics",
                message="缺少估值数据，无法计算估值因子和估值异常过滤。",
                details={"required_date": score_date, "latest_date": None},
            )
        )
        return

    if latest_date < score_date:
        issues.append(
            DataQualityIssue(
                level="warning",
                code="stale_valuation_metrics",
                message="估值数据早于评分日，估值因子可能滞后。",
                details={"required_date": score_date, "latest_date": latest_date},
            )
        )

    missing_count = _count(
        connection,
        """
        select count(*) as count
        from valuation_metrics
        where trade_date = ?
          and (pe is null or pb is null)
        """,
        (latest_date,),
    )
    if missing_count:
        issues.append(
            DataQualityIssue(
                level="warning",
                code="missing_valuation_fields",
                message="部分估值记录缺少 PE 或 PB 字段。",
                details={"trade_date": latest_date, "rows_count": missing_count},
            )
        )


def _check_financial_metrics(
    connection: sqlite3.Connection,
    score_date: str,
    issues: list[DataQualityIssue],
) -> None:
    latest_date = _latest_date(connection, "financial_metrics", "report_date")
    if latest_date is None:
        issues.append(
            DataQualityIssue(
                level="error",
                code="missing_financial_metrics",
                message="缺少财务数据，无法计算质量和成长因子。",
                details={"required_date": score_date, "latest_date": None},
            )
        )
        return

    if (_parse_date(score_date) - _parse_date(latest_date)).days > 180:
        issues.append(
            DataQualityIssue(
                level="warning",
                code="stale_financial_metrics",
                message="财务报告期距离评分日较久，质量和成长因子可能滞后。",
                details={"score_date": score_date, "latest_report_date": latest_date},
            )
        )

    future_disclosure_count = _count(
        connection,
        """
        select count(*) as count
        from financial_metrics
        where disclosure_date > ?
        """,
        (score_date,),
    )
    if future_disclosure_count:
        issues.append(
            DataQualityIssue(
                level="error",
                code="future_disclosure",
                message="存在披露日期晚于评分日的财务数据，继续使用会产生未来函数风险。",
                details={"score_date": score_date, "rows_count": future_disclosure_count},
            )
        )


def _latest_date(connection: sqlite3.Connection, table: str, column: str) -> str | None:
    row = connection.execute(f"select max({column}) as latest_date from {table}").fetchone()
    return row["latest_date"] if row and row["latest_date"] else None


def _count(
    connection: sqlite3.Connection,
    query: str,
    params: tuple[Any, ...] = (),
) -> int:
    row = connection.execute(query, params).fetchone()
    return int(row["count"]) if row else 0


def _parse_date(value: str) -> date:
    if len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise ValueError(f"invalid date: {value}")
    return date.fromisoformat(value)
