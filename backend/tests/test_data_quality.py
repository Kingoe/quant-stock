from __future__ import annotations


def test_quality_report_returns_errors_for_empty_database(tmp_path) -> None:
    """测试空库会返回明确的数据缺口。"""
    from app.data.quality import generate_data_quality_report
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        report = generate_data_quality_report(connection, score_date="2026-05-12")

    assert report.status == "error"
    assert report.summary["error"] >= 3
    issue_codes = {issue.code for issue in report.issues}
    assert "missing_daily_prices" in issue_codes
    assert "missing_valuation_metrics" in issue_codes
    assert "missing_financial_metrics" in issue_codes


def test_quality_report_passes_for_complete_recent_data(tmp_path) -> None:
    """测试关键数据完整且新鲜时质量报告通过。"""
    from app.data.quality import generate_data_quality_report
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        _insert_stock(connection, "000001")
        _insert_daily_price(connection, "000001", "2026-05-12")
        _insert_valuation(connection, "000001", "2026-05-12")
        _insert_financial(connection, "000001", "2026-03-31", "2026-04-25")

        report = generate_data_quality_report(connection, score_date="2026-05-12")

    assert report.status == "ok"
    assert report.summary == {"error": 0, "warning": 0, "info": 0}
    assert report.issues == []


def test_quality_report_flags_stale_and_missing_fields(tmp_path) -> None:
    """测试过期数据、缺失估值字段和异常行情字段会被识别。"""
    from app.data.quality import generate_data_quality_report
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        _insert_stock(connection, "000001")
        _insert_daily_price(connection, "000001", "2026-05-10", amount=0)
        _insert_valuation(connection, "000001", "2026-05-10", pe=None)
        _insert_financial(connection, "000001", "2025-09-30", "2025-10-28")

        report = generate_data_quality_report(connection, score_date="2026-05-12")

    issue_codes = {issue.code for issue in report.issues}
    assert report.status == "error"
    assert "stale_daily_prices" in issue_codes
    assert "stale_valuation_metrics" in issue_codes
    assert "missing_valuation_fields" in issue_codes
    assert "abnormal_daily_price_fields" in issue_codes
    assert "stale_financial_metrics" in issue_codes


def test_quality_report_flags_future_financial_disclosure(tmp_path) -> None:
    """测试财务披露日期晚于评分日会被识别为未来函数风险。"""
    from app.data.quality import generate_data_quality_report
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        _insert_stock(connection, "000001")
        _insert_daily_price(connection, "000001", "2026-05-12")
        _insert_valuation(connection, "000001", "2026-05-12")
        _insert_financial(connection, "000001", "2026-03-31", "2026-05-20")

        report = generate_data_quality_report(connection, score_date="2026-05-12")

    assert report.status == "error"
    future_issue = next(issue for issue in report.issues if issue.code == "future_disclosure")
    assert future_issue.level == "error"
    assert future_issue.details["rows_count"] == 1


def _insert_stock(connection, stock_code: str) -> None:
    connection.execute(
        """
        insert into stocks (stock_code, stock_name, exchange, list_date, industry, is_st, status)
        values (?, ?, ?, ?, ?, ?, ?)
        """,
        (stock_code, "测试股票", "SZSE", "2020-01-01", "测试行业", 0, "active"),
    )


def _insert_daily_price(
    connection,
    stock_code: str,
    trade_date: str,
    amount: float = 1000000,
) -> None:
    connection.execute(
        """
        insert into daily_prices (
            stock_code, trade_date, open_price, high_price, low_price, close_price,
            volume, amount, adjusted_close, is_suspended, is_limit_up, is_limit_down
        )
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (stock_code, trade_date, 10, 11, 9, 10.5, 1000, amount, 10.5, 0, 0, 0),
    )


def _insert_valuation(
    connection,
    stock_code: str,
    trade_date: str,
    pe: float | None = 12.5,
) -> None:
    connection.execute(
        """
        insert into valuation_metrics (stock_code, trade_date, pe, pb, ps, dividend_yield)
        values (?, ?, ?, ?, ?, ?)
        """,
        (stock_code, trade_date, pe, 1.2, 2.0, 0.03),
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
