from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class StorageError(ValueError):
    """Raised when storage configuration is invalid."""


def sqlite_path_from_url(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise StorageError("database_url must start with sqlite:///")

    raw_path = database_url[len(prefix) :]
    if not raw_path:
        raise StorageError("database_url must include a SQLite file path")

    if raw_path.startswith("/"):
        return Path(raw_path)
    return Path(raw_path)


@contextmanager
def open_sqlite_connection(database_url: str) -> Iterator[sqlite3.Connection]:
    database_path = sqlite_path_from_url(database_url)
    if database_path.parent != Path("."):
        database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
