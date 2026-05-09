from app.data import (
    StockBasicRecord,
    ValuationRecord,
    calculate_valuation_factor,
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

        scores = calculate_valuation_factor(connection, ["600000", "000001", "600519"], "2026-05-07")

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
            connection, ["600000", "000001", "600519"], "2026-05-07", pe_weight=0.0, pb_weight=0.0, dividend_yield_weight=1.0
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

        scores = calculate_valuation_factor(connection, ["600000", "000001", "600519"], "2026-05-07")

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