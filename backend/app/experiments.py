from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParameterExperimentCreate:
    name: str
    description: str | None
    parameters: Mapping[str, Any]
    metrics: Mapping[str, Any]
    notes: str | None = None


@dataclass(frozen=True)
class ParameterExperiment:
    experiment_id: int
    name: str
    description: str | None
    parameters: dict[str, Any]
    metrics: dict[str, Any]
    notes: str | None
    created_at: str


def record_parameter_experiment(
    connection: sqlite3.Connection,
    experiment: ParameterExperimentCreate,
) -> ParameterExperiment:
    name = experiment.name.strip()
    if not name:
        raise ValueError("name must not be empty")

    parameters_json = _dump_json_payload("parameters", experiment.parameters)
    metrics_json = _dump_json_payload("metrics", experiment.metrics)

    cursor = connection.execute(
        """
        insert into parameter_experiments (
            name, description, parameters, metrics, notes
        ) values (?, ?, ?, ?, ?)
        """,
        (
            name,
            experiment.description,
            parameters_json,
            metrics_json,
            experiment.notes,
        ),
    )
    created = get_parameter_experiment(connection, cursor.lastrowid)
    if created is None:
        raise RuntimeError("failed to load created parameter experiment")
    return created


def get_parameter_experiment(
    connection: sqlite3.Connection,
    experiment_id: int,
) -> ParameterExperiment | None:
    row = connection.execute(
        """
        select *
        from parameter_experiments
        where experiment_id = ?
        """,
        (experiment_id,),
    ).fetchone()
    if row is None:
        return None
    return _row_to_experiment(row)


def list_parameter_experiments(
    connection: sqlite3.Connection,
    *,
    limit: int = 20,
) -> list[ParameterExperiment]:
    if limit <= 0:
        raise ValueError("limit must be greater than 0")

    rows = connection.execute(
        """
        select *
        from parameter_experiments
        order by created_at desc, experiment_id desc
        limit ?
        """,
        (limit,),
    ).fetchall()
    return [_row_to_experiment(row) for row in rows]


def _dump_json_payload(field_name: str, payload: Mapping[str, Any]) -> str:
    try:
        return json.dumps(dict(payload), ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be JSON serializable") from exc


def _row_to_experiment(row: sqlite3.Row) -> ParameterExperiment:
    return ParameterExperiment(
        experiment_id=row["experiment_id"],
        name=row["name"],
        description=row["description"],
        parameters=json.loads(row["parameters"]),
        metrics=json.loads(row["metrics"]),
        notes=row["notes"],
        created_at=row["created_at"],
    )
