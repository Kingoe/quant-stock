from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.data.quality import DataQualityIssue, generate_data_quality_report


@dataclass(frozen=True)
class StrategyPreflightResult:
    """策略运行前置检查结果。"""

    status: str
    can_run: bool
    score_date: str
    summary: dict[str, int]
    blocking_issues: list[DataQualityIssue]
    warning_issues: list[DataQualityIssue]


def generate_strategy_preflight(
    connection: sqlite3.Connection,
    score_date: str,
) -> StrategyPreflightResult:
    """生成策略运行前置检查结果。"""
    quality_report = generate_data_quality_report(connection, score_date=score_date)
    blocking_issues = [issue for issue in quality_report.issues if issue.level == "error"]
    warning_issues = [issue for issue in quality_report.issues if issue.level == "warning"]

    if blocking_issues:
        status = "blocked"
        can_run = False
    elif warning_issues:
        status = "warning"
        can_run = True
    else:
        status = "passed"
        can_run = True

    return StrategyPreflightResult(
        status=status,
        can_run=can_run,
        score_date=score_date,
        summary=quality_report.summary,
        blocking_issues=blocking_issues,
        warning_issues=warning_issues,
    )
