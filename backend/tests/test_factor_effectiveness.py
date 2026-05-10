import pytest

from app.data import (
    DailyPriceRecord,
    calculate_forward_returns,
    calculate_information_coefficient,
    calculate_layer_returns,
    load_daily_prices,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_calculate_forward_returns_uses_adjusted_close_and_future_price(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_daily_prices(
            connection,
            [
                DailyPriceRecord("000001", "2026-05-07", 10, 10, 10, 10, 100, 1000, 100),
                DailyPriceRecord("000001", "2026-05-12", 11, 11, 11, 11, 100, 1100, 112),
                DailyPriceRecord("000002", "2026-05-07", 20, 20, 20, 20, 100, 2000, 20),
                DailyPriceRecord("000002", "2026-05-08", 19, 19, 19, 19, 100, 1900, 19),
                DailyPriceRecord("000003", "2026-05-07", 30, 30, 30, 30, 100, 3000, 30),
            ],
        )

        returns = calculate_forward_returns(
            connection, ["000001", "000002", "000003"], "2026-05-07", holding_days=5
        )

    assert returns == {
        "000001": pytest.approx(0.12),
        "000002": pytest.approx(-0.05),
    }


def test_calculate_information_coefficient_aligns_scores_and_returns() -> None:
    result = calculate_information_coefficient(
        {"000001": 0.9, "000002": 0.7, "000003": 0.2, "000004": 0.1},
        {"000001": 0.10, "000002": 0.06, "000003": -0.02, "000099": 0.50},
    )

    assert result.sample_size == 3
    assert result.ic == pytest.approx(0.9986, abs=0.0001)
    assert result.rank_ic == pytest.approx(1.0)


def test_calculate_information_coefficient_returns_none_for_constant_factor() -> None:
    result = calculate_information_coefficient(
        {"000001": 0.5, "000002": 0.5, "000003": 0.5},
        {"000001": 0.10, "000002": 0.03, "000003": -0.02},
    )

    assert result.sample_size == 3
    assert result.ic is None
    assert result.rank_ic is None


def test_calculate_layer_returns_splits_by_factor_score_descending() -> None:
    layers = calculate_layer_returns(
        {"000001": 0.9, "000002": 0.8, "000003": 0.2, "000004": 0.1},
        {"000001": 0.10, "000002": 0.06, "000003": -0.02, "000004": -0.04},
        layers=2,
    )

    assert [(layer.layer, layer.stock_count) for layer in layers] == [(1, 2), (2, 2)]
    assert layers[0].average_factor_score == pytest.approx(0.85)
    assert layers[0].average_forward_return == pytest.approx(0.08)
    assert layers[1].average_factor_score == pytest.approx(0.15)
    assert layers[1].average_forward_return == pytest.approx(-0.03)


def test_factor_effectiveness_rejects_invalid_arguments(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="holding_days"):
            calculate_forward_returns(connection, ["000001"], "2026-05-07", holding_days=0)

    with pytest.raises(ValueError, match="layers"):
        calculate_layer_returns({"000001": 0.9}, {"000001": 0.1}, layers=0)
