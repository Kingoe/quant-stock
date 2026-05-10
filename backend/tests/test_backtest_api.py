from __future__ import annotations

from app.storage import initialize_schema, open_sqlite_connection


def test_get_backtest_summary_empty_db() -> None:
    """测试空数据库返回默认指标。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        from app.backtest.api import get_backtest_summary

        result = get_backtest_summary(database_url, "1")

        assert "data" in result
        assert "meta" in result
        assert result["data"]["core_metrics"]["total_return"] == 0.0
        assert result["data"]["core_metrics"]["annual_return"] == 0.0
        assert result["data"]["core_metrics"]["max_drawdown"] == 0.0
        assert result["data"]["core_metrics"]["sharpe_ratio"] is None
        assert result["data"]["core_metrics"]["turnover_rate"] == 0.0
        assert result["data"]["core_metrics"]["win_rate"] is None


def test_get_backtest_summary_follows_api_convention() -> None:
    """测试遵循 data + meta 响应约定。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        from app.backtest.api import get_backtest_summary

        result = get_backtest_summary(database_url, "1")

        assert set(result.keys()) == {"data", "meta"}
        assert isinstance(result["meta"], dict)


def test_get_equity_curve_empty_db() -> None:
    """测试空数据库返回空曲线。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        from app.backtest.api import get_equity_curve

        result = get_equity_curve(database_url, "1")

        assert result["data"]["equity_curve"] == []


def test_get_equity_curve_follows_api_convention() -> None:
    """测试净值曲线遵循 API 约定。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        from app.backtest.api import get_equity_curve

        result = get_equity_curve(database_url, "1")

        assert "data" in result
        assert "equity_curve" in result["data"]
        assert isinstance(result["data"]["equity_curve"], list)


def test_get_drawdown_curve_empty_db() -> None:
    """测试空数据库返回空回撤曲线。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        from app.backtest.api import get_drawdown_curve

        result = get_drawdown_curve(database_url, "1")

        assert result["data"]["drawdown"] == []


def test_get_drawdown_curve_follows_api_convention() -> None:
    """测试回撤曲线遵循 API 约定。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        from app.backtest.api import get_drawdown_curve

        result = get_drawdown_curve(database_url, "1")

        assert "data" in result
        assert "drawdown" in result["data"]
        assert isinstance(result["data"]["drawdown"], list)


def test_get_backtest_summary_custom_risk_free_rate() -> None:
    """测试自定义无风险利率。"""
    database_url = "sqlite:///:memory:"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        from app.backtest.api import get_backtest_summary

        result = get_backtest_summary(database_url, "1", risk_free_rate=0.05)

        assert result["data"]["core_metrics"]["total_return"] == 0.0
        # 仅验证参数传递正常，不影响默认值
