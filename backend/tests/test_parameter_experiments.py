import pytest

from app.experiments import (
    ParameterExperimentCreate,
    get_parameter_experiment,
    list_parameter_experiments,
    record_parameter_experiment,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_record_parameter_experiment_persists_parameters_and_metrics(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        experiment = record_parameter_experiment(
            connection,
            ParameterExperimentCreate(
                name="估值权重提升实验",
                description="提高估值权重，观察回撤是否下降",
                parameters={
                    "factor_weights": {"valuation": 0.35, "quality": 0.25, "growth": 0.15},
                    "limit": 20,
                },
                metrics={"annual_return": 0.12, "max_drawdown": -0.08, "sharpe": 1.15},
                notes="仅使用固定样例数据，不作为实盘依据",
            ),
        )

        loaded = get_parameter_experiment(connection, experiment.experiment_id)

    assert loaded is not None
    assert loaded.experiment_id == experiment.experiment_id
    assert loaded.name == "估值权重提升实验"
    assert loaded.parameters["factor_weights"]["valuation"] == pytest.approx(0.35)
    assert loaded.parameters["limit"] == 20
    assert loaded.metrics["max_drawdown"] == pytest.approx(-0.08)
    assert loaded.notes == "仅使用固定样例数据，不作为实盘依据"
    assert loaded.created_at


def test_list_parameter_experiments_returns_newest_first_and_limit(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        first = record_parameter_experiment(
            connection,
            ParameterExperimentCreate(
                name="实验 A",
                description=None,
                parameters={"limit": 10},
                metrics={"total_return": 0.05},
                notes=None,
            ),
        )
        second = record_parameter_experiment(
            connection,
            ParameterExperimentCreate(
                name="实验 B",
                description=None,
                parameters={"limit": 20},
                metrics={"total_return": 0.08},
                notes=None,
            ),
        )

        experiments = list_parameter_experiments(connection, limit=1)

    assert [experiment.experiment_id for experiment in experiments] == [second.experiment_id]
    assert first.experiment_id < second.experiment_id


def test_record_parameter_experiment_rejects_empty_name(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="name"):
            record_parameter_experiment(
                connection,
                ParameterExperimentCreate(
                    name=" ",
                    description=None,
                    parameters={"limit": 20},
                    metrics={"total_return": 0.08},
                    notes=None,
                ),
            )


def test_record_parameter_experiment_rejects_non_json_payload(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="JSON"):
            record_parameter_experiment(
                connection,
                ParameterExperimentCreate(
                    name="非法参数实验",
                    description=None,
                    parameters={"bad": object()},
                    metrics={"total_return": 0.08},
                    notes=None,
                ),
            )


def test_list_parameter_experiments_rejects_invalid_limit(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="limit"):
            list_parameter_experiments(connection, limit=0)
