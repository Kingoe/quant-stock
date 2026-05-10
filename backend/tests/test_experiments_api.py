from __future__ import annotations


def test_experiments_endpoint_returns_recent_experiments(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.experiments import ParameterExperimentCreate, record_parameter_experiment
    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        record_parameter_experiment(
            connection,
            ParameterExperimentCreate(
                name="实验 A",
                description="估值权重测试",
                parameters={"limit": 10},
                metrics={"total_return": 0.05},
                notes="第一轮",
            ),
        )
        second = record_parameter_experiment(
            connection,
            ParameterExperimentCreate(
                name="实验 B",
                description=None,
                parameters={"limit": 20},
                metrics={"total_return": 0.08, "max_drawdown": -0.03},
                notes=None,
            ),
        )

    client = TestClient(app)
    response = client.get("/api/experiments", params={"database_url": database_url, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"data", "meta"}
    assert len(body["data"]) == 1
    assert body["data"][0]["experiment_id"] == second.experiment_id
    assert body["data"][0]["name"] == "实验 B"
    assert body["data"][0]["parameters"]["limit"] == 20
    assert body["data"][0]["metrics"]["total_return"] == 0.08
    assert body["meta"]["request_id"] == "local-dev"


def test_experiment_detail_endpoint_returns_single_experiment(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.experiments import ParameterExperimentCreate, record_parameter_experiment
    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        experiment = record_parameter_experiment(
            connection,
            ParameterExperimentCreate(
                name="估值权重提升实验",
                description="提高估值权重",
                parameters={"factor_weights": {"valuation": 0.35}},
                metrics={"annual_return": 0.12},
                notes="仅用于复盘",
            ),
        )

    client = TestClient(app)
    response = client.get(
        f"/api/experiments/{experiment.experiment_id}",
        params={"database_url": database_url},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["experiment_id"] == experiment.experiment_id
    assert body["data"]["name"] == "估值权重提升实验"
    assert body["data"]["description"] == "提高估值权重"
    assert body["data"]["parameters"]["factor_weights"]["valuation"] == 0.35
    assert body["data"]["metrics"]["annual_return"] == 0.12
    assert body["data"]["notes"] == "仅用于复盘"
    assert body["data"]["created_at"]


def test_experiment_detail_endpoint_returns_404_for_missing_experiment(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get("/api/experiments/999", params={"database_url": database_url})

    assert response.status_code == 404
    assert response.json()["detail"] == "experiment not found"


def test_experiments_endpoint_validates_limit(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.storage import initialize_schema, open_sqlite_connection

    database_url = f"sqlite:///{tmp_path / 'quant.db'}"
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

    client = TestClient(app)
    response = client.get("/api/experiments", params={"database_url": database_url, "limit": 0})

    assert response.status_code == 422
