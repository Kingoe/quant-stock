from __future__ import annotations

from unittest.mock import patch

from app.portfolio import RebalanceRecommendation
from app.reports.weekly import generate_weekly_html_report


def test_generate_weekly_html_report_contains_html_structure() -> None:
    """测试生成的 HTML 包含基本结构。"""
    mock_recommendations = [
        RebalanceRecommendation(
            stock_code="000001",
            stock_name="平安银行",
            action="buy",
            target_weight=0.08,
            total_score=0.75,
            rank=1,
            reason="新增目标持仓",
            risk_note=None,
        ),
    ]

    with patch("app.reports.weekly.generate_weekly_rebalance", return_value=mock_recommendations):
        html = generate_weekly_html_report(
            "sqlite:///:memory:",
            "000906",
            "2026-05-10",
        )

    assert "<!DOCTYPE html>" in html
    assert '<html lang="zh-CN">' in html
    assert "<head>" in html
    assert "<body>" in html
    assert "量化选股周报" in html
    assert "2026-05-10" in html


def test_generate_weekly_html_report_with_buy_list() -> None:
    """测试买入列表正确渲染。"""
    mock_recommendations = [
        RebalanceRecommendation(
            stock_code="000001",
            stock_name="平安银行",
            action="buy",
            target_weight=0.08,
            total_score=0.75,
            rank=1,
            reason="新增目标持仓",
            risk_note=None,
        ),
    ]

    with patch("app.reports.weekly.generate_weekly_rebalance", return_value=mock_recommendations):
        html = generate_weekly_html_report(
            "sqlite:///:memory:",
            "000906",
            "2026-05-10",
        )

    assert "买入列表" in html
    assert "000001" in html
    assert "平安银行" in html
    assert "8.00%" in html


def test_generate_weekly_html_report_with_risk_note() -> None:
    """测试风险提示正确渲染。"""
    mock_recommendations = [
        RebalanceRecommendation(
            stock_code="000001",
            stock_name="平安银行",
            action="buy",
            target_weight=0.08,
            total_score=0.75,
            rank=1,
            reason="新增目标持仓",
            risk_note="涨停无法买入",
        ),
    ]

    with patch("app.reports.weekly.generate_weekly_rebalance", return_value=mock_recommendations):
        html = generate_weekly_html_report(
            "sqlite:///:memory:",
            "000906",
            "2026-05-10",
        )

    assert "涨停无法买入" in html
    assert "⚠" in html


def test_generate_weekly_html_report_with_sell_list() -> None:
    """测试卖出列表正确渲染。"""
    mock_recommendations = [
        RebalanceRecommendation(
            stock_code="000002",
            stock_name="万科A",
            action="sell",
            target_weight=None,
            total_score=0.60,
            rank=None,
            reason="已不在目标组合中",
            risk_note=None,
        ),
    ]

    with patch("app.reports.weekly.generate_weekly_rebalance", return_value=mock_recommendations):
        html = generate_weekly_html_report(
            "sqlite:///:memory:",
            "000906",
            "2026-05-10",
        )

    assert "卖出列表" in html
    assert "000002" in html
    assert "万科A" in html


def test_generate_weekly_html_report_empty_recommendations() -> None:
    """测试空调仓建议时的 HTML 生成。"""
    with patch("app.reports.weekly.generate_weekly_rebalance", return_value=[]):
        html = generate_weekly_html_report(
            "sqlite:///:memory:",
            "000906",
            "2026-05-10",
        )

    assert "<!DOCTYPE html>" in html
    assert "量化选股周报" in html
    assert "报告生成时间" in html


def test_generate_weekly_html_report_styles_included() -> None:
    """测试样式包含在 HTML 中。"""
    with patch("app.reports.weekly.generate_weekly_rebalance", return_value=[]):
        html = generate_weekly_html_report(
            "sqlite:///:memory:",
            "000906",
            "2026-05-10",
        )

    assert "<style>" in html
    assert "body {" in html
    assert "table {" in html
