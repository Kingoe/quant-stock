from __future__ import annotations

from unittest.mock import patch


def test_rebalance_html_endpoint() -> None:
    """测试 HTML 报告端点。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.portfolio import RebalanceRecommendation

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
        client = TestClient(app)
        response = client.get(
            "/api/rebalance/html",
            params={
                "index_code": "000906",
                "score_date": "2026-05-10",
                "database_url": "sqlite:///:memory:",
            },
        )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "量化选股周报" in response.text
    assert "买入列表" in response.text
    assert "000001" in response.text


def test_rebalance_excel_endpoint() -> None:
    """测试 Excel 报告端点。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.portfolio import RebalanceRecommendation

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

    with patch("app.main.generate_weekly_rebalance", return_value=mock_recommendations):
        client = TestClient(app)
        response = client.get(
            "/api/rebalance/excel",
            params={
                "index_code": "000906",
                "score_date": "2026-05-10",
                "database_url": "sqlite:///:memory:",
            },
        )

    assert response.status_code == 200
    assert "application/vnd.openxmlformats" in response.headers["content-type"]
    assert len(response.content) > 0


def test_rebalance_csv_endpoint() -> None:
    """测试 CSV 报告端点。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.portfolio import RebalanceRecommendation

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

    with patch("app.main.generate_weekly_rebalance", return_value=mock_recommendations):
        client = TestClient(app)
        response = client.get(
            "/api/rebalance/csv",
            params={
                "index_code": "000906",
                "score_date": "2026-05-10",
                "database_url": "sqlite:///:memory:",
            },
        )

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "股票代码,股票名称,操作,目标仓位,总分,排名,原因,风险提示" in response.text
    assert "000001" in response.text
