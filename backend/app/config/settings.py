from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when a configuration file is missing required or valid values."""


@dataclass(frozen=True)
class AppSettings:
    name: str
    environment: str
    timezone: str
    database_url: str


@dataclass(frozen=True)
class FactorWeights:
    valuation: float
    quality: float
    growth: float
    momentum: float
    risk_liquidity: float

    def validate(self) -> None:
        total = (
            self.valuation
            + self.quality
            + self.growth
            + self.momentum
            + self.risk_liquidity
        )
        if abs(total - 1.0) > 0.000001:
            raise ConfigError("factor weights must sum to 1")
        for name, value in self.__dict__.items():
            if value < 0:
                raise ConfigError(f"{name} factor weight must be non-negative")


@dataclass(frozen=True)
class StrategySettings:
    universe: str
    rebalance_frequency: str
    holding_count: int
    single_stock_max_weight: float
    industry_max_weight: float
    cash_buffer: float
    factor_weights: FactorWeights

    def validate(self) -> None:
        if self.holding_count <= 0:
            raise ConfigError("holding_count must be positive")
        _validate_ratio("single_stock_max_weight", self.single_stock_max_weight)
        _validate_ratio("industry_max_weight", self.industry_max_weight)
        _validate_ratio("cash_buffer", self.cash_buffer)
        if self.single_stock_max_weight * self.holding_count < 1:
            raise ConfigError("single_stock_max_weight is too low for holding_count")
        self.factor_weights.validate()


@dataclass(frozen=True)
class TradingCostSettings:
    commission_rate: float
    stamp_duty_rate: float
    slippage_rate: float

    def validate(self) -> None:
        _validate_non_negative("commission_rate", self.commission_rate)
        _validate_non_negative("stamp_duty_rate", self.stamp_duty_rate)
        _validate_non_negative("slippage_rate", self.slippage_rate)


@dataclass(frozen=True)
class Settings:
    app: AppSettings
    strategy: StrategySettings
    trading_cost: TradingCostSettings


def load_settings(path: str | Path) -> Settings:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"config file does not exist: {config_path}")

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    settings = Settings(
        app=_load_app_settings(_required_mapping(data, "app")),
        strategy=_load_strategy_settings(_required_mapping(data, "strategy")),
        trading_cost=_load_trading_cost_settings(_required_mapping(data, "trading_cost")),
    )
    settings.strategy.validate()
    settings.trading_cost.validate()
    return settings


def _load_app_settings(data: dict[str, Any]) -> AppSettings:
    return AppSettings(
        name=_required_str(data, "name"),
        environment=_required_str(data, "environment"),
        timezone=_required_str(data, "timezone"),
        database_url=_required_str(data, "database_url"),
    )


def _load_strategy_settings(data: dict[str, Any]) -> StrategySettings:
    factor_weights = _required_mapping(data, "factor_weights")
    return StrategySettings(
        universe=_required_str(data, "universe"),
        rebalance_frequency=_required_str(data, "rebalance_frequency"),
        holding_count=_required_int(data, "holding_count"),
        single_stock_max_weight=_required_float(data, "single_stock_max_weight"),
        industry_max_weight=_required_float(data, "industry_max_weight"),
        cash_buffer=_required_float(data, "cash_buffer"),
        factor_weights=FactorWeights(
            valuation=_required_float(factor_weights, "valuation"),
            quality=_required_float(factor_weights, "quality"),
            growth=_required_float(factor_weights, "growth"),
            momentum=_required_float(factor_weights, "momentum"),
            risk_liquidity=_required_float(factor_weights, "risk_liquidity"),
        ),
    )


def _load_trading_cost_settings(data: dict[str, Any]) -> TradingCostSettings:
    return TradingCostSettings(
        commission_rate=_required_float(data, "commission_rate"),
        stamp_duty_rate=_required_float(data, "stamp_duty_rate"),
        slippage_rate=_required_float(data, "slippage_rate"),
    )


def _required_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a table")
    return value


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ConfigError(f"{key} must be an integer")
    return value


def _required_float(data: dict[str, Any], key: str) -> float:
    value = data.get(key)
    if not isinstance(value, int | float):
        raise ConfigError(f"{key} must be a number")
    return float(value)


def _validate_ratio(name: str, value: float) -> None:
    if value <= 0 or value >= 1:
        raise ConfigError(f"{name} must be greater than 0 and less than 1")


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ConfigError(f"{name} must be non-negative")
