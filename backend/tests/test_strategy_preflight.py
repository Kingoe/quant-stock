from __future__ import annotations


def test_strategy_preflight_blocks_when_quality_report_has_errors(tmp_path) -> None:
    """测试数据质量存在 error 时前置检查会阻止策略运行。"""
    from app.storage import initialize_schema, open_sqlite_connection
    from app.strategy.preflight import generate_strategy_preflight

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        preflight = generate_strategy_preflight(connection, score_date="2026-05-12")

    assert preflight.status == "blocked"
    assert preflight.can_run is False
    assert preflight.summary["error"] >= 3
    assert any(issue.code == "missing_daily_prices" for issue in preflight.blocking_issues)


def test_strategy_preflight_allows_run_with_warnings(tmp_path) -> None:
    """测试只有 warning 时前置检查允许策略运行并返回风险提示。"""
    from app.storage import initialize_schema, open_sqlite_connection
    from app.strategy.preflight import generate_strategy_preflight

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        _insert_stock(connection, "000001")
        _insert_daily_price(connection, "000001", "2026-05-12")
        _insert_valuation(connection, "000001", "2026-05-10")
        _insert_financial(connection, "000001", "2026-03-31", "2026-04-25")

        preflight = generate_strategy_preflight(connection, score_date="2026-05-12")

    assert preflight.status == "warning"
    assert preflight.can_run is True
    assert preflight.blocking_issues == []
    assert any(issue.code == "stale_valuation_metrics" for issue in preflight.warning_issues)


def test_strategy_preflight_passes_when_quality_report_is_ok(tmp_path) -> None:
    """测试关键数据完整时前置检查通过。"""
    from app.storage import initialize_schema, open_sqlite_connection
    from app.strategy.preflight import generate_strategy_preflight

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        _insert_stock(connection, "000001")
        _insert_daily_price(connection, "000001", "2026-05-12")
        _insert_valuation(connection, "000001", "2026-05-12")
        _insert_financial(connection, "000001", "2026-03-31", "2026-04-25")

        preflight = generate_strategy_preflight(connection, score_date="2026-05-12")

    assert preflight.status == "passed"
    assert preflight.can_run is True
    assert preflight.summary == {"error": 0, "warning": 0, "info": 0}
    assert preflight.blocking_issues == []
    assert preflight.warning_issues == []


def _insert_stock(connection, stock_code: str) -> None:
    connection.execute(
        """
        insert into stocks (stock_code, stock_name, exchange, list_date, industry, is_st, status)
        values (?, ?, ?, ?, ?, ?, ?)
        """,
        (stock_code, "测试股票", "SZSE", "2020-01-01", "测试行业", 0, "active"),
    )


def _insert_daily_price(connection, stock_code: str, trade_date: str) -> None:
    connection.execute(
        """
        insert into daily_prices (
            stock_code, trade_date, open_price, high_price, low_price, close_price,
            volume, amount, adjusted_close, is_suspended, is_limit_up, is_limit_down
        )
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (stock_code, trade_date, 10, 11, 9, 10.5, 1000, 1000000, 10.5, 0, 0, 0),
    )


def _insert_valuation(connection, stock_code: str, trade_date: str) -> None:
    connection.execute(
        """
        insert into valuation_metrics (stock_code, trade_date, pe, pb, ps, dividend_yield)
        values (?, ?, ?, ?, ?, ?)
        """,
        (stock_code, trade_date, 12.5, 1.2, 2.0, 0.03),
    )


def _insert_financial(
    connection,
    stock_code: str,
    report_date: str,
    disclosure_date: str,
) -> None:
    connection.execute(
        """
        insert into financial_metrics (
            stock_code, report_date, disclosure_date, roe, gross_margin,
            revenue_growth, net_profit_growth, operating_cash_flow, net_profit
        )
        values (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (stock_code, report_date, disclosure_date, 0.12, 0.45, 0.08, 0.1, 1000, 800),
    )
