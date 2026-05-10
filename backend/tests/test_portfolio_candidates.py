import pytest

from app.data import (
    DailyPriceRecord,
    FinancialRecord,
    StockBasicRecord,
    ValuationRecord,
    load_daily_prices,
    load_financial_metrics,
    load_stock_basics,
    load_valuations,
)
from app.portfolio import (
    apply_single_stock_weight_limit,
    calculate_target_positions,
    calculate_top_candidates,
    select_top_candidates,
)
from app.storage import initialize_schema, open_sqlite_connection
from tests.test_factor_calculators import _build_amount_records


def test_select_top_candidates_orders_by_total_score_descending() -> None:
    candidates = select_top_candidates(
        ["600000", "000001", "600519"],
        {
            "600000": 0.7,
            "000001": 0.9,
            "600519": 0.6,
        },
        limit=2,
    )

    assert [candidate.stock_code for candidate in candidates] == ["000001", "600000"]
    assert [candidate.rank for candidate in candidates] == [1, 2]
    assert candidates[0].total_score == 0.9


def test_select_top_candidates_uses_stock_code_as_stable_tiebreaker() -> None:
    candidates = select_top_candidates(
        ["600519", "000001", "600000"],
        {
            "600519": 0.8,
            "000001": 0.8,
            "600000": 0.8,
        },
        limit=3,
    )

    assert [candidate.stock_code for candidate in candidates] == ["000001", "600000", "600519"]


def test_select_top_candidates_ignores_stocks_without_total_score() -> None:
    candidates = select_top_candidates(
        ["600000", "000001", "600519"],
        {
            "600000": 0.7,
            "600519": 0.9,
        },
        limit=3,
    )

    assert [candidate.stock_code for candidate in candidates] == ["600519", "600000"]


def test_select_top_candidates_rejects_non_positive_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        select_top_candidates(["600000"], {"600000": 0.7}, limit=0)


def test_calculate_top_candidates_uses_total_factor_scores(tmp_path) -> None:
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
                ValuationRecord("600000", "2026-05-20", 5.0, 0.8, None, 0.05),
                ValuationRecord("000001", "2026-05-20", 20.0, 2.0, None, 0.01),
                ValuationRecord("600519", "2026-05-20", 30.0, 5.0, None, 0.01),
            ],
        )
        load_financial_metrics(
            connection,
            [
                FinancialRecord(
                    "600000", "2026-03-31", "2026-04-25", 20.0, 40.0, 20.0, 20.0, 2000.0, 1000.0
                ),
                FinancialRecord(
                    "000001", "2026-03-31", "2026-04-25", 5.0, 20.0, 5.0, 5.0, 300.0, 300.0
                ),
                FinancialRecord(
                    "600519", "2026-03-31", "2026-04-25", 4.0, 15.0, 3.0, 3.0, 200.0, 300.0
                ),
            ],
        )
        load_daily_prices(
            connection,
            _build_amount_records(
                {
                    "600000": 30_000_000.0,
                    "000001": 10_000_000.0,
                    "600519": 5_000_000.0,
                },
                "2026-05-01",
            )
            + [
                DailyPriceRecord("600000", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("000001", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600519", "2026-03-21", 0, 0, 0, 10.0, 100, 1000, 10.0),
                DailyPriceRecord("600000", "2026-01-20", 0, 0, 0, 9.0, 100, 900, 9.0),
                DailyPriceRecord("000001", "2026-01-20", 0, 0, 0, 11.0, 100, 1100, 11.0),
                DailyPriceRecord("600519", "2026-01-20", 0, 0, 0, 12.0, 100, 1200, 12.0),
            ],
        )

        candidates = calculate_top_candidates(
            connection,
            ["600000", "000001", "600519"],
            "2026-05-20",
            limit=2,
        )

    assert [candidate.stock_code for candidate in candidates] == ["600000", "000001"]
    assert [candidate.rank for candidate in candidates] == [1, 2]


def test_apply_single_stock_weight_limit_caps_equal_weight_positions() -> None:
    candidates = select_top_candidates(
        ["600000", "000001", "600519"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
        },
        limit=3,
    )

    positions = apply_single_stock_weight_limit(candidates, single_stock_max_weight=0.08)

    assert [position.stock_code for position in positions] == ["600000", "000001", "600519"]
    assert [position.rank for position in positions] == [1, 2, 3]
    assert all(position.target_weight == 0.08 for position in positions)
    assert positions[0].total_score == 0.9


def test_apply_single_stock_weight_limit_keeps_equal_weight_below_cap() -> None:
    candidates = select_top_candidates(
        ["600000", "000001", "600519", "300750", "601318"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
            "300750": 0.6,
            "601318": 0.5,
        },
        limit=5,
    )

    positions = apply_single_stock_weight_limit(candidates, single_stock_max_weight=0.3)

    assert all(position.target_weight == 0.2 for position in positions)


def test_apply_single_stock_weight_limit_rejects_invalid_cap() -> None:
    candidates = select_top_candidates(["600000"], {"600000": 0.9}, limit=1)

    with pytest.raises(ValueError, match="single_stock_max_weight must be greater than 0"):
        apply_single_stock_weight_limit(candidates, single_stock_max_weight=0)

    with pytest.raises(ValueError, match="single_stock_max_weight must be less than or equal to 1"):
        apply_single_stock_weight_limit(candidates, single_stock_max_weight=1.2)


def test_calculate_target_positions_selects_candidates_and_applies_single_stock_cap() -> None:
    positions = calculate_target_positions(
        ["600000", "000001", "600519"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
        },
        limit=2,
        single_stock_max_weight=0.4,
    )

    assert [position.stock_code for position in positions] == ["600000", "000001"]
    assert [position.target_weight for position in positions] == [0.4, 0.4]
