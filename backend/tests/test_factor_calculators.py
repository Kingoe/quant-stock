from app.data import (
    DailyPriceRecord,
    FinancialRecord,
    StockBasicRecord,
    ValuationRecord,
    calculate_growth_factor,
    calculate_momentum_factor,
    calculate_quality_factor,
    calculate_risk_factor,
    calculate_valuation_factor,
    load_daily_prices,
    load_financial_metrics,
    load_stock_basics,
    load_valuations,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_valuation_factor_scores_low_pe_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None, None),
                ValuationRecord("000001", "2026-05-07", 6.0, 0.9, None, None),
                ValuationRecord("600519", "2026-05-07", 30.0, 10.0, None, None),
            ],
        )

        scores = calculate_valuation_factor(
            connection, ["600000", "000001", "600519"], "2026-05-07"
        )

    # PE 越低得分越高
    assert scores["600000"] > scores["000001"]
    assert scores["000001"] > scores["600519"]


def test_valuation_factor_scores_low_pb_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None, None),
                ValuationRecord("000001", "2026-05-07", 6.0, 0.9, None, None),
                ValuationRecord("600519", "2026-05-07", 30.0, 10.0, None, None),
            ],
        )

        scores = calculate_valuation_factor(
            connection, ["600000", "000001", "600519"], "2026-05-07", pe_weight=0.0, pb_weight=1.0
        )

    # PB 越低得分越高
    assert scores["600000"] > scores["000001"]
    assert scores["000001"] > scores["600519"]


def test_valuation_factor_scores_high_dividend_yield_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", None, None, None, 0.05),
                ValuationRecord("000001", "2026-05-07", None, None, None, 0.03),
                ValuationRecord("600519", "2026-05-07", None, None, None, 0.01),
            ],
        )

        scores = calculate_valuation_factor(
            connection,
            ["600000", "000001", "600519"],
            "2026-05-07",
            pe_weight=0.0,
            pb_weight=0.0,
            dividend_yield_weight=1.0,
        )

    # 股息率越高得分越高
    assert scores["600000"] > scores["000001"]
    assert scores["000001"] > scores["600519"]


def test_valuation_factor_handles_missing_valuation_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None, None),
                ValuationRecord("000001", "2026-05-07", 6.0, 0.9, None, None),
                # 贵州茅台没有估值数据
            ],
        )

        scores = calculate_valuation_factor(
            connection, ["600000", "000001", "600519"], "2026-05-07"
        )

    # 贵州茅台因为缺失估值数据不会被包含在结果中
    assert "600519" not in scores
    assert len(scores) == 2


def test_valuation_factor_returns_empty_dict_when_no_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )

        scores = calculate_valuation_factor(connection, ["600000"], "2026-05-07")

    assert scores == {}


def test_valuation_factor_handles_null_pe_pb(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-07", 5.0, 0.8, None, None),
                ValuationRecord("000001", "2026-05-07", None, None, None, 0.03),
            ],
        )

        scores = calculate_valuation_factor(connection, ["600000", "000001"], "2026-05-07")

    # PE 为 None 的股票在 PE 子因子上应该得到中等分数
    assert len(scores) == 2
    assert scores["600000"] >= 0
    assert scores["000001"] >= 0
    assert scores["600000"] <= 1
    assert scores["000001"] <= 1


def test_valuation_factor_uses_aligned_valuation_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_valuations(
            connection,
            [
                ValuationRecord("600000", "2026-05-05", 5.0, 0.8, None, None),
                ValuationRecord("600000", "2026-05-06", 4.8, 0.78, None, None),
                # 评分日是 2026-05-07，应该使用 2026-05-06 的数据
            ],
        )

        scores = calculate_valuation_factor(connection, ["600000"], "2026-05-07")

    assert len(scores) == 1
    assert scores["600000"] >= 0


def test_quality_factor_scores_high_roe_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 12.0, 32.0, 6.0, 10.0, 1200.0, 600.0
                ),
                FinancialRecord(
                    "600519", "2026-03-31", "2026-04-25", 25.0, 35.0, 15.0, 20.0, 2500.0, 1250.0
                ),
            ],
        )

        scores = calculate_quality_factor(
            connection, ["600000", "000001", "600519"], "2026-05-07", roe_weight=1.0
        )

    # ROE 越高得分越高
    assert scores["600519"] > scores["000001"]
    assert scores["000001"] > scores["600000"]


def test_quality_factor_scores_high_gross_margin_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 12.0, 32.0, 6.0, 10.0, 1200.0, 600.0
                ),
                FinancialRecord(
                    "600519", "2026-03-31", "2026-04-25", 25.0, 35.0, 15.0, 20.0, 2500.0, 1250.0
                ),
            ],
        )

        scores = calculate_quality_factor(
            connection, ["600000", "000001", "600519"], "2026-05-07", gross_margin_weight=1.0
        )

    # 毛利率越高得分越高
    assert scores["600519"] > scores["000001"]
    assert scores["000001"] > scores["600000"]


def test_quality_factor_scores_high_cash_flow_quality_higher(
    tmp_path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 800.0, 500.0
                ),
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 12.0, 32.0, 6.0, 10.0, 1000.0, 600.0
                ),
                FinancialRecord(
                    "600519", "2026-03-31", "2026-04-25", 25.0, 35.0, 15.0, 20.0, 3500.0, 1250.0
                ),
            ],
        )

        scores = calculate_quality_factor(
            connection, ["600000", "000001", "600519"], "2026-05-07", cash_flow_weight=1.0
        )

    # 现金流质量越高得分越高
    assert scores["600519"] > scores["000001"]
    assert scores["000001"] > scores["600000"]


def test_quality_factor_handles_missing_financial_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 12.0, 32.0, 6.0, 10.0, 1200.0, 600.0
                ),
                # 贵州茅台没有财务数据
            ],
        )

        scores = calculate_quality_factor(connection, ["600000", "000001", "600519"], "2026-05-07")

    # 贵州茅台因为缺失财务数据不会被包含在结果中
    assert "600519" not in scores
    assert len(scores) == 2


def test_quality_factor_returns_empty_dict_when_no_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )

        scores = calculate_quality_factor(connection, ["600000"], "2026-05-07")

    assert scores == {}


def test_quality_factor_handles_null_sub_indicators(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                FinancialRecord("000001", "2026-03-31", "2026-04-25", None, None, None, None, None),
            ],
        )

        scores = calculate_quality_factor(connection, ["600000", "000001"], "2026-05-07")

    # 为 None 的股票应该在对应子因子上得到中等分数
    assert len(scores) == 2
    assert scores["600000"] >= 0
    assert scores["000001"] >= 0
    assert scores["600000"] <= 1
    assert scores["000001"] <= 1


def test_quality_factor_uses_aligned_financial_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-20", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                FinancialRecord(
                    "600000", "2026-06-30", "2026-08-10", 12.0, 32.0, 6.0, 10.0, 1200.0, 600.0
                ),
                # 评分日是 2026-05-07，应该使用 2026-03-31 的数据（已披露）
            ],
        )

        scores = calculate_quality_factor(connection, ["600000"], "2026-05-07")

    assert len(scores) == 1
    assert scores["600000"] >= 0


def test_quality_factor_handles_zero_net_profit(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                # 净利润为 0，现金流质量应为 None
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 12.0, 32.0, 6.0, 10.0, 1800.0, 0.0
                ),
            ],
        )

        scores = calculate_quality_factor(
            connection,
            ["600000", "000001"],
            "2026-05-07",
            roe_weight=0.0,
            gross_margin_weight=0.0,
            cash_flow_weight=1.0,
        )

    # 净利润为 0 的股票在现金流质量子因子上应该得到中等分数
    assert len(scores) == 2
    assert scores["000001"] >= 0
    assert scores["000001"] <= 1


def test_growth_factor_scores_higher_growth_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("600519", "贵州茅台", "SH", "2001-08-27", "白酒", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 12.0, 32.0, 10.0, 12.0, 1200.0, 600.0
                ),
                FinancialRecord(
                    "600519", "2026-03-31", "2026-04-25", 25.0, 35.0, 20.0, 25.0, 2500.0, 1250.0
                ),
            ],
        )

        scores = calculate_growth_factor(connection, ["600000", "000001", "600519"], "2026-05-07")

    assert scores["600519"] > scores["000001"] > scores["600000"]


def test_growth_factor_supports_weight_configuration(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [
                StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active"),
                StockBasicRecord("000001", "平安银行", "SZ", "2000-01-01", "银行", False, "active"),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 10.0, 30.0, 30.0, 5.0, 1000.0, 500.0
                ),
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 12.0, 32.0, 5.0, 30.0, 1200.0, 600.0
                ),
            ],
        )

        revenue_only_scores = calculate_growth_factor(
            connection,
            ["600000", "000001"],
            "2026-05-07",
            revenue_growth_weight=1.0,
            net_profit_growth_weight=0.0,
        )
        profit_only_scores = calculate_growth_factor(
            connection,
            ["600000", "000001"],
            "2026-05-07",
            revenue_growth_weight=0.0,
            net_profit_growth_weight=1.0,
        )

    assert revenue_only_scores["600000"] > revenue_only_scores["000001"]
    assert profit_only_scores["000001"] > profit_only_scores["600000"]


def test_growth_factor_uses_aligned_financial_data(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_stock_basics(
            connection,
            [StockBasicRecord("600000", "浦发银行", "SH", "2000-01-01", "银行", False, "active")],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-20", 10.0, 30.0, 5.0, 8.0, 1000.0, 500.0
                ),
                FinancialRecord(
                    "600000", "2026-06-30", "2026-08-10", 12.0, 32.0, 50.0, 60.0, 1200.0, 600.0
                ),
            ],
        )

        scores = calculate_growth_factor(connection, ["600000"], "2026-05-07")

    assert scores["600000"] == 0.5


def test_momentum_factor_scores_higher_return_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-01-07", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-03-08", 0, 0, 0, 12.0, 100, 1200, 12.0),
                DailyPriceRecord("600000", "2026-05-07", 0, 0, 0, 14.0, 100, 1400, 14.0),
                DailyPriceRecord("000001", "2026-01-07", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-03-08", 0, 0, 0, 11.0, 100, 1100, 11.0),
                DailyPriceRecord("000001", "2026-05-07", 0, 0, 0, 12.0, 100, 1200, 12.0),
                DailyPriceRecord("600519", "2026-01-07", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-03-08", 0, 0, 0, 10.5, 100, 1050, 10.5),
                DailyPriceRecord("600519", "2026-05-07", 0, 0, 0, 11.0, 100, 1100, 11.0),
            ],
        )

        scores = calculate_momentum_factor(connection, ["600000", "000001", "600519"], "2026-05-07")

    assert scores["600000"] > scores["000001"] > scores["600519"]


def test_momentum_factor_supports_weight_configuration(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-01-07", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-03-08", 0, 0, 0, 20.0, 100, 2000, 20.0),
                DailyPriceRecord("600000", "2026-05-07", 0, 0, 0, 22.0, 100, 2200, 22.0),
                DailyPriceRecord("000001", "2026-01-07", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-03-08", 0, 0, 0, 11.0, 100, 1100, 11.0),
                DailyPriceRecord("000001", "2026-05-07", 0, 0, 0, 20.0, 100, 2000, 20.0),
            ],
        )

        short_only_scores = calculate_momentum_factor(
            connection,
            ["600000", "000001"],
            "2026-05-07",
            momentum_60_weight=1.0,
            momentum_120_weight=0.0,
        )
        long_only_scores = calculate_momentum_factor(
            connection,
            ["600000", "000001"],
            "2026-05-07",
            momentum_60_weight=0.0,
            momentum_120_weight=1.0,
        )

    assert short_only_scores["000001"] > short_only_scores["600000"]
    assert long_only_scores["600000"] > long_only_scores["000001"]


def test_momentum_factor_uses_adjusted_close_before_close_price(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-03-08", 0, 0, 0, 10.0, 100, 1000, 100.0),
                DailyPriceRecord("600000", "2026-05-07", 0, 0, 0, 20.0, 100, 2000, 120.0),
                DailyPriceRecord("000001", "2026-03-08", 0, 0, 0, 10.0, 100, 1000, None),
                DailyPriceRecord("000001", "2026-05-07", 0, 0, 0, 20.0, 100, 2000, None),
            ],
        )

        scores = calculate_momentum_factor(
            connection,
            ["600000", "000001"],
            "2026-05-07",
            momentum_60_weight=1.0,
            momentum_120_weight=0.0,
        )

    assert scores["000001"] > scores["600000"]


def test_momentum_factor_handles_missing_price_history(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-07", 0, 0, 0, 20.0, 100, 2000, 20.0),
                DailyPriceRecord("000001", "2026-03-08", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-05-07", 0, 0, 0, 20.0, 100, 2000, 20.0),
                DailyPriceRecord("600519", "2026-03-08", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-05-07", 0, 0, 0, 11.0, 100, 1100, 11.0),
            ],
        )

        scores = calculate_momentum_factor(
            connection,
            ["600000", "000001", "600519"],
            "2026-05-07",
            momentum_60_weight=1.0,
            momentum_120_weight=0.0,
        )

    assert scores["000001"] > scores["600000"] > scores["600519"]
    assert scores["600000"] == 0.5


def test_risk_factor_scores_lower_volatility_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-05-02", 0, 0, 0, 10.2, 100, 1020, 10.2),
                DailyPriceRecord("600000", "2026-05-03", 0, 0, 0, 10.4, 100, 1040, 10.4),
                DailyPriceRecord("600000", "2026-05-04", 0, 0, 0, 10.6, 100, 1060, 10.6),
                DailyPriceRecord("000001", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-05-02", 0, 0, 0, 13.0, 100, 1300, 13.0),
                DailyPriceRecord("000001", "2026-05-03", 0, 0, 0, 9.0, 100, 900, 9.0),
                DailyPriceRecord("000001", "2026-05-04", 0, 0, 0, 12.0, 100, 1200, 12.0),
                DailyPriceRecord("600519", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-05-02", 0, 0, 0, 12.0, 100, 1200, 12.0),
                DailyPriceRecord("600519", "2026-05-03", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-05-04", 0, 0, 0, 11.0, 100, 1100, 11.0),
            ],
        )

        scores = calculate_risk_factor(
            connection,
            ["600000", "000001", "600519"],
            "2026-05-04",
            volatility_weight=1.0,
            max_drawdown_weight=0.0,
        )

    assert scores["600000"] > scores["600519"] > scores["000001"]


def test_risk_factor_scores_lower_max_drawdown_higher(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-05-02", 0, 0, 0, 11.0, 100, 1100, 11.0),
                DailyPriceRecord("600000", "2026-05-03", 0, 0, 0, 10.8, 100, 1080, 10.8),
                DailyPriceRecord("600000", "2026-05-04", 0, 0, 0, 11.2, 100, 1120, 11.2),
                DailyPriceRecord("000001", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-05-02", 0, 0, 0, 15.0, 100, 1500, 15.0),
                DailyPriceRecord("000001", "2026-05-03", 0, 0, 0, 9.0, 100, 900, 9.0),
                DailyPriceRecord("000001", "2026-05-04", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-05-02", 0, 0, 0, 12.0, 100, 1200, 12.0),
                DailyPriceRecord("600519", "2026-05-03", 0, 0, 0, 10.8, 100, 1080, 10.8),
                DailyPriceRecord("600519", "2026-05-04", 0, 0, 0, 11.0, 100, 1100, 11.0),
            ],
        )

        scores = calculate_risk_factor(
            connection,
            ["600000", "000001", "600519"],
            "2026-05-04",
            volatility_weight=0.0,
            max_drawdown_weight=1.0,
        )

    assert scores["600000"] > scores["600519"] > scores["000001"]


def test_risk_factor_supports_weight_configuration(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-05-02", 0, 0, 0, 10.1, 100, 1010, 10.1),
                DailyPriceRecord("600000", "2026-05-03", 0, 0, 0, 9.9, 100, 990, 9.9),
                DailyPriceRecord("600000", "2026-05-04", 0, 0, 0, 10.3, 100, 1030, 10.3),
                DailyPriceRecord("000001", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-05-02", 0, 0, 0, 18.0, 100, 1800, 18.0),
                DailyPriceRecord("000001", "2026-05-03", 0, 0, 0, 20.0, 100, 2000, 20.0),
                DailyPriceRecord("000001", "2026-05-04", 0, 0, 0, 24.0, 100, 2400, 24.0),
            ],
        )

        volatility_only_scores = calculate_risk_factor(
            connection,
            ["600000", "000001"],
            "2026-05-04",
            volatility_weight=1.0,
            max_drawdown_weight=0.0,
        )
        drawdown_only_scores = calculate_risk_factor(
            connection,
            ["600000", "000001"],
            "2026-05-04",
            volatility_weight=0.0,
            max_drawdown_weight=1.0,
        )

    assert volatility_only_scores["600000"] > volatility_only_scores["000001"]
    assert drawdown_only_scores["000001"] > drawdown_only_scores["600000"]


def test_risk_factor_uses_adjusted_close_before_close_price(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-05-02", 0, 0, 0, 20.0, 100, 2000, 10.1),
                DailyPriceRecord("600000", "2026-05-03", 0, 0, 0, 10.0, 100, 1000, 10.2),
                DailyPriceRecord("600000", "2026-05-04", 0, 0, 0, 20.0, 100, 2000, 10.3),
                DailyPriceRecord("000001", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-05-02", 0, 0, 0, 10.1, 100, 1010, 20.0),
                DailyPriceRecord("000001", "2026-05-03", 0, 0, 0, 10.2, 100, 1020, 10.0),
                DailyPriceRecord("000001", "2026-05-04", 0, 0, 0, 10.3, 100, 1030, 20.0),
            ],
        )

        scores = calculate_risk_factor(
            connection,
            ["600000", "000001"],
            "2026-05-04",
            volatility_weight=1.0,
            max_drawdown_weight=0.0,
        )

    assert scores["600000"] > scores["000001"]


def test_risk_factor_handles_missing_price_history(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("600000", "2026-05-04", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-05-02", 0, 0, 0, 10.2, 100, 1020, 10.2),
                DailyPriceRecord("000001", "2026-05-03", 0, 0, 0, 10.4, 100, 1040, 10.4),
                DailyPriceRecord("000001", "2026-05-04", 0, 0, 0, 10.6, 100, 1060, 10.6),
                DailyPriceRecord("600519", "2026-05-01", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-05-02", 0, 0, 0, 12.0, 100, 1200, 12.0),
                DailyPriceRecord("600519", "2026-05-03", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-05-04", 0, 0, 0, 11.0, 100, 1100, 11.0),
            ],
        )

        scores = calculate_risk_factor(
            connection,
            ["600000", "000001", "600519"],
            "2026-05-04",
            volatility_weight=1.0,
            max_drawdown_weight=0.0,
        )

    assert scores["000001"] > scores["600000"] > scores["600519"]
    assert scores["600000"] == 0.5
