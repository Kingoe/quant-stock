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
    TradingStatus,
    add_trading_availability_notes,
    apply_industry_weight_limit,
    apply_single_stock_weight_limit,
    calculate_target_positions,
    calculate_top_candidates,
    generate_rebalance_recommendations,
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


def test_apply_industry_weight_limit_caps_industry_total_by_rank() -> None:
    positions = calculate_target_positions(
        ["600000", "000001", "600519"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
        },
        limit=3,
        single_stock_max_weight=0.2,
    )

    capped_positions = apply_industry_weight_limit(
        positions,
        {"600000": "银行", "000001": "银行", "600519": "白酒"},
        industry_max_weight=0.3,
    )

    assert [position.stock_code for position in capped_positions] == ["600000", "000001", "600519"]
    assert [position.target_weight for position in capped_positions] == pytest.approx(
        [0.2, 0.1, 0.2]
    )


def test_apply_industry_weight_limit_keeps_industry_below_cap() -> None:
    positions = calculate_target_positions(
        ["600000", "000001", "600519"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
        },
        limit=3,
        single_stock_max_weight=0.1,
    )

    capped_positions = apply_industry_weight_limit(
        positions,
        {"600000": "银行", "000001": "银行", "600519": "白酒"},
        industry_max_weight=0.3,
    )

    assert [position.target_weight for position in capped_positions] == [0.1, 0.1, 0.1]


def test_apply_industry_weight_limit_rejects_invalid_cap() -> None:
    positions = calculate_target_positions(
        ["600000"],
        {"600000": 0.9},
        limit=1,
        single_stock_max_weight=0.2,
    )

    with pytest.raises(ValueError, match="industry_max_weight must be greater than 0"):
        apply_industry_weight_limit(positions, {"600000": "银行"}, industry_max_weight=0)

    with pytest.raises(ValueError, match="industry_max_weight must be less than or equal to 1"):
        apply_industry_weight_limit(positions, {"600000": "银行"}, industry_max_weight=1.2)


def test_generate_rebalance_recommendations_buy_list() -> None:
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

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions=None,
        stock_names={"600000": "浦发银行", "000001": "平安银行"},
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7},
        top_candidates=None,
    )

    buy_list = [r for r in recommendations if r.action == "buy"]
    assert len(buy_list) == 2
    assert sorted([r.stock_code for r in buy_list]) == ["000001", "600000"]
    assert buy_list[0].target_weight == 0.4
    assert buy_list[0].reason == "新增目标持仓"


def test_generate_rebalance_recommendations_sell_list() -> None:
    positions = calculate_target_positions(
        ["600000", "000001"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
        },
        limit=2,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions={"600000": 0.1, "600519": 0.2},
        stock_names={"600000": "浦发银行", "600519": "贵州茅台"},
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7},
        top_candidates=None,
    )

    sell_list = [r for r in recommendations if r.action == "sell"]
    assert len(sell_list) == 1
    assert sell_list[0].stock_code == "600519"
    assert sell_list[0].reason == "已不在目标组合中"
    assert sell_list[0].target_weight is None


def test_generate_rebalance_recommendations_hold_list() -> None:
    positions = calculate_target_positions(
        ["600000", "000001", "600519"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
        },
        limit=3,
        single_stock_max_weight=0.3,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions={"600000": 0.1, "000001": 0.1},
        stock_names={"600000": "浦发银行", "000001": "平安银行", "600519": "贵州茅台"},
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7},
        top_candidates=None,
    )

    hold_list = [r for r in recommendations if r.action == "hold"]
    assert len(hold_list) == 2
    assert sorted([r.stock_code for r in hold_list]) == ["000001", "600000"]
    assert hold_list[0].reason == "继续持有"


def test_generate_rebalance_recommendations_watch_list() -> None:
    positions = calculate_target_positions(
        ["600000", "000001", "600519"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
            "300750": 0.6,
            "601318": 0.5,
        },
        limit=3,
        single_stock_max_weight=0.3,
    )

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

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions=None,
        stock_names={"300750": "宁德时代", "601318": "中国平安"},
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7, "300750": 0.6, "601318": 0.5},
        top_candidates=candidates,
    )

    watch_list = [r for r in recommendations if r.action == "watch"]
    assert len(watch_list) == 2
    assert [r.stock_code for r in watch_list] == ["300750", "601318"]
    assert watch_list[0].reason == "高分观察股"
    assert watch_list[0].target_weight is None


def test_generate_rebalance_recommendations_orders_by_action() -> None:
    positions = calculate_target_positions(
        ["600000", "000001"],
        {
            "600000": 0.9,
            "000001": 0.8,
        },
        limit=2,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions={"600519": 0.2},
        stock_names={"600000": "浦发银行", "000001": "平安银行", "600519": "贵州茅台"},
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7},
        top_candidates=None,
    )

    assert len(recommendations) == 3
    assert recommendations[0].action == "buy"
    assert recommendations[1].action == "buy"
    assert recommendations[2].action == "sell"


def test_generate_rebalance_recommendations_handles_empty_inputs() -> None:
    recommendations = generate_rebalance_recommendations(
        target_positions=[],
        current_positions=None,
        stock_names={},
        total_scores={},
        top_candidates=None,
    )

    assert len(recommendations) == 0


def test_generate_rebalance_recommendations_mixed_scenario() -> None:
    positions = calculate_target_positions(
        ["600000", "000001", "600519"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
            "300750": 0.6,
        },
        limit=3,
        single_stock_max_weight=0.3,
    )

    candidates = select_top_candidates(
        ["600000", "000001", "600519", "300750"],
        {
            "600000": 0.9,
            "000001": 0.8,
            "600519": 0.7,
            "300750": 0.6,
        },
        limit=4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions={"600000": 0.1, "300750": 0.1},
        stock_names={
            "600000": "浦发银行",
            "000001": "平安银行",
            "600519": "贵州茅台",
            "300750": "宁德时代",
        },
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7, "300750": 0.6},
        top_candidates=candidates,
    )

    actions = [r.action for r in recommendations]
    assert "buy" in actions
    assert "hold" in actions
    assert "sell" in actions
    assert "watch" in actions

    assert any(r.stock_code == "300750" and r.action == "sell" for r in recommendations)
    assert any(r.stock_code == "000001" and r.action == "buy" for r in recommendations)
    assert any(r.stock_code == "600000" and r.action == "hold" for r in recommendations)
    assert any(r.stock_code == "300750" and r.action == "watch" for r in recommendations)


def test_add_trading_availability_notes_limit_up_blocks_buy() -> None:
    positions = calculate_target_positions(
        ["600000", "000001"],
        {"600000": 0.9, "000001": 0.8},
        limit=2,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions=None,
        stock_names={"600000": "浦发银行", "000001": "平安银行"},
        total_scores={"600000": 0.9, "000001": 0.8},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(
        recommendations,
        {"600000": TradingStatus(is_limit_up=True)},
    )

    assert any(
        r.stock_code == "600000" and r.risk_note == "涨停无法买入" for r in updated
    )
    assert all(r.stock_code != "600000" or r.risk_note for r in updated if r.action == "buy")


def test_add_trading_availability_notes_limit_down_blocks_sell() -> None:
    positions = calculate_target_positions(
        ["600000", "000001"],
        {"600000": 0.9, "000001": 0.8},
        limit=2,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions={"600519": 0.2},
        stock_names={"600000": "浦发银行", "000001": "平安银行", "600519": "贵州茅台"},
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(
        recommendations,
        {"600519": TradingStatus(is_limit_down=True)},
    )

    assert any(
        r.stock_code == "600519" and r.risk_note == "跌停无法卖出" for r in updated
    )


def test_add_trading_availability_notes_suspension_blocks_both() -> None:
    positions = calculate_target_positions(
        ["600000", "000001"],
        {"600000": 0.9, "000001": 0.8},
        limit=2,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions={"600519": 0.2},
        stock_names={"600000": "浦发银行", "000001": "平安银行", "600519": "贵州茅台"},
        total_scores={"600000": 0.9, "000001": 0.8, "600519": 0.7},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(
        recommendations,
        {"600519": TradingStatus(is_suspended=True)},
    )

    assert any(
        r.stock_code == "600519" and r.risk_note == "停牌无法交易" for r in updated
    )


def test_add_trading_availability_notes_limit_down_does_not_block_buy() -> None:
    positions = calculate_target_positions(
        ["600000"],
        {"600000": 0.9},
        limit=1,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions=None,
        stock_names={"600000": "浦发银行"},
        total_scores={"600000": 0.9},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(
        recommendations,
        {"600000": TradingStatus(is_limit_down=True)},
    )

    assert not any(r.risk_note for r in updated)


def test_add_trading_availability_notes_limit_up_does_not_block_sell() -> None:
    positions = calculate_target_positions(
        ["600000"],
        {"600000": 0.9},
        limit=1,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions={"000001": 0.2},
        stock_names={"600000": "浦发银行", "000001": "平安银行"},
        total_scores={"600000": 0.9, "000001": 0.8},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(
        recommendations,
        {"000001": TradingStatus(is_limit_up=True)},
    )

    assert not any(r.risk_note for r in updated)


def test_add_trading_availability_notes_appends_to_existing_risk_note() -> None:
    positions = calculate_target_positions(
        ["600000"],
        {"600000": 0.9},
        limit=1,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions=None,
        stock_names={"600000": "浦发银行"},
        total_scores={"600000": 0.9},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(
        recommendations,
        {"600000": TradingStatus(is_suspended=True)},
    )

    assert updated[0].risk_note == "停牌无法交易"


def test_add_trading_availability_notes_preserves_other_fields() -> None:
    positions = calculate_target_positions(
        ["600000"],
        {"600000": 0.9},
        limit=1,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions=None,
        stock_names={"600000": "浦发银行"},
        total_scores={"600000": 0.9},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(
        recommendations,
        {"600000": TradingStatus(is_limit_up=True)},
    )

    assert updated[0].stock_code == recommendations[0].stock_code
    assert updated[0].stock_name == recommendations[0].stock_name
    assert updated[0].action == recommendations[0].action
    assert updated[0].target_weight == recommendations[0].target_weight
    assert updated[0].total_score == recommendations[0].total_score
    assert updated[0].rank == recommendations[0].rank
    assert updated[0].reason == recommendations[0].reason


def test_add_trading_availability_notes_handles_missing_status() -> None:
    positions = calculate_target_positions(
        ["600000"],
        {"600000": 0.9},
        limit=1,
        single_stock_max_weight=0.4,
    )

    recommendations = generate_rebalance_recommendations(
        target_positions=positions,
        current_positions=None,
        stock_names={"600000": "浦发银行"},
        total_scores={"600000": 0.9},
        top_candidates=None,
    )

    updated = add_trading_availability_notes(recommendations, {})

    assert len(updated) == len(recommendations)
    assert not any(r.risk_note for r in updated)
