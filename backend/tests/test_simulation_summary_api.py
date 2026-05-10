from __future__ import annotations


def test_simulation_summary_endpoint_returns_account_and_execution_data(tmp_path) -> None:
    """测试模拟运行摘要端点返回账户和信号执行数据。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.portfolio import RebalanceRecommendation
    from app.simulation import create_signals, record_execution
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        connection.execute(
            """
            insert into portfolio_snapshots (run_id, run_date, cash, total_value)
            values
                (1, '2026-05-08', 100000, 100000),
                (1, '2026-05-09', 92000, 104000),
                (1, '2026-05-10', 88000, 102000)
            """
        )
        signals = create_signals(
            connection,
            [
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
                RebalanceRecommendation(
                    stock_code="600000",
                    stock_name="浦发银行",
                    action="sell",
                    target_weight=None,
                    total_score=0.60,
                    rank=None,
                    reason="已不在目标组合中",
                    risk_note="跌停无法卖出",
                ),
            ],
            "2026-05-10",
        )
        record_execution(connection, signals[0].id, "000001", "buy", 100, 10.5, "filled")

    client = TestClient(app)
    response = client.get(
        "/api/simulation/summary",
        params={"database_url": database_url, "run_date": "2026-05-10"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["account"]["latest_value"] == 102000
    assert body["data"]["account"]["cash"] == 88000
    assert body["data"]["account"]["total_return"] == 2.0
    assert body["data"]["performance"]["max_drawdown"] == 1.9231
    assert body["data"]["execution"]["total_signals"] == 2
    assert body["data"]["execution"]["executed_signals"] == 1
    assert body["data"]["execution"]["pending_signals"] == 1
    assert body["data"]["latest_date"] == "2026-05-10"
    assert "meta" in body


def test_simulation_summary_endpoint_returns_empty_state(tmp_path) -> None:
    """测试模拟运行摘要端点在无数据时返回稳定空状态。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get("/api/simulation/summary", params={"database_url": database_url})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["account"]["latest_value"] == 0
    assert body["data"]["account"]["total_return"] == 0
    assert body["data"]["execution"]["total_signals"] == 0
    assert body["data"]["latest_date"] is None
