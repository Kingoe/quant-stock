from pathlib import Path

import pytest

from app.config import ConfigError, load_settings


def test_load_settings_reads_application_and_strategy_config(tmp_path: Path) -> None:
    config_file = tmp_path / "settings.toml"
    config_file.write_text(
        """
[app]
name = "Quant Stock"
environment = "test"
timezone = "Asia/Shanghai"
database_url = "sqlite:///data/test.db"

[strategy]
universe = "CSI800"
rebalance_frequency = "weekly"
holding_count = 15
single_stock_max_weight = 0.08
industry_max_weight = 0.25
cash_buffer = 0.05

[strategy.factor_weights]
valuation = 0.25
quality = 0.25
growth = 0.20
momentum = 0.20
risk_liquidity = 0.10

[trading_cost]
commission_rate = 0.0003
stamp_duty_rate = 0.0005
slippage_rate = 0.001
""",
        encoding="utf-8",
    )

    settings = load_settings(config_file)

    assert settings.app.name == "Quant Stock"
    assert settings.app.environment == "test"
    assert settings.app.timezone == "Asia/Shanghai"
    assert settings.app.database_url == "sqlite:///data/test.db"
    assert settings.strategy.universe == "CSI800"
    assert settings.strategy.rebalance_frequency == "weekly"
    assert settings.strategy.holding_count == 15
    assert settings.strategy.single_stock_max_weight == 0.08
    assert settings.strategy.industry_max_weight == 0.25
    assert settings.strategy.cash_buffer == 0.05
    assert settings.strategy.factor_weights.valuation == 0.25
    assert settings.strategy.factor_weights.risk_liquidity == 0.10
    assert settings.trading_cost.commission_rate == 0.0003
    assert settings.trading_cost.stamp_duty_rate == 0.0005
    assert settings.trading_cost.slippage_rate == 0.001


def test_load_settings_rejects_factor_weights_that_do_not_sum_to_one(tmp_path: Path) -> None:
    config_file = tmp_path / "settings.toml"
    config_file.write_text(
        """
[app]
name = "Quant Stock"
environment = "test"
timezone = "Asia/Shanghai"
database_url = "sqlite:///data/test.db"

[strategy]
universe = "CSI800"
rebalance_frequency = "weekly"
holding_count = 15
single_stock_max_weight = 0.08
industry_max_weight = 0.25
cash_buffer = 0.05

[strategy.factor_weights]
valuation = 0.30
quality = 0.25
growth = 0.20
momentum = 0.20
risk_liquidity = 0.10

[trading_cost]
commission_rate = 0.0003
stamp_duty_rate = 0.0005
slippage_rate = 0.001
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="factor weights must sum to 1"):
        load_settings(config_file)


def test_load_settings_rejects_invalid_holding_count(tmp_path: Path) -> None:
    config_file = tmp_path / "settings.toml"
    config_file.write_text(
        """
[app]
name = "Quant Stock"
environment = "test"
timezone = "Asia/Shanghai"
database_url = "sqlite:///data/test.db"

[strategy]
universe = "CSI800"
rebalance_frequency = "weekly"
holding_count = 0
single_stock_max_weight = 0.08
industry_max_weight = 0.25
cash_buffer = 0.05

[strategy.factor_weights]
valuation = 0.25
quality = 0.25
growth = 0.20
momentum = 0.20
risk_liquidity = 0.10

[trading_cost]
commission_rate = 0.0003
stamp_duty_rate = 0.0005
slippage_rate = 0.001
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="holding_count must be positive"):
        load_settings(config_file)


def test_load_settings_reads_default_config_file() -> None:
    config_file = Path(__file__).resolve().parents[1] / "config" / "default.toml"

    settings = load_settings(config_file)

    assert settings.app.environment == "local"
    assert settings.strategy.universe == "CSI800"
    assert settings.strategy.rebalance_frequency == "weekly"
