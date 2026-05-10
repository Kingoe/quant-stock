import pytest

from app.data import neutralize_scores_by_industry


def test_neutralize_scores_by_industry_ranks_stocks_within_each_industry() -> None:
    scores = {
        "600000": 0.95,
        "000001": 0.80,
        "300750": 0.60,
        "002594": 0.40,
    }
    industries = {
        "600000": "银行",
        "000001": "银行",
        "300750": "新能源",
        "002594": "新能源",
    }

    neutralized = neutralize_scores_by_industry(scores, industries)

    assert neutralized == {
        "600000": pytest.approx(1.0),
        "000001": pytest.approx(0.0),
        "300750": pytest.approx(1.0),
        "002594": pytest.approx(0.0),
    }


def test_neutralize_scores_by_industry_handles_ties_with_average_rank() -> None:
    neutralized = neutralize_scores_by_industry(
        {"600000": 0.80, "000001": 0.80, "601398": 0.50},
        {"600000": "银行", "000001": "银行", "601398": "银行"},
    )

    assert neutralized["600000"] == pytest.approx(0.75)
    assert neutralized["000001"] == pytest.approx(0.75)
    assert neutralized["601398"] == pytest.approx(0.0)


def test_neutralize_scores_by_industry_uses_neutral_score_for_small_industry() -> None:
    neutralized = neutralize_scores_by_industry(
        {"600000": 0.95, "300750": 0.60, "002594": 0.40},
        {"600000": "银行", "300750": "新能源", "002594": "新能源"},
    )

    assert neutralized["600000"] == pytest.approx(0.5)
    assert neutralized["300750"] == pytest.approx(1.0)
    assert neutralized["002594"] == pytest.approx(0.0)


def test_neutralize_scores_by_industry_groups_missing_industry_as_unknown() -> None:
    neutralized = neutralize_scores_by_industry(
        {"600000": 0.95, "000001": 0.80},
        {"600000": None},
    )

    assert neutralized["600000"] == pytest.approx(1.0)
    assert neutralized["000001"] == pytest.approx(0.0)


def test_neutralize_scores_by_industry_rejects_invalid_min_industry_size() -> None:
    with pytest.raises(ValueError, match="min_industry_size"):
        neutralize_scores_by_industry({"600000": 0.95}, {"600000": "银行"}, min_industry_size=0)
