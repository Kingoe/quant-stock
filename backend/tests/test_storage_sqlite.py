import sqlite3
from pathlib import Path

import pytest

from app.storage import StorageError, open_sqlite_connection, sqlite_path_from_url


def test_sqlite_path_from_url_accepts_relative_path() -> None:
    path = sqlite_path_from_url("sqlite:///data/quant.db")

    assert path == Path("data/quant.db")


def test_sqlite_path_from_url_accepts_absolute_path() -> None:
    path = sqlite_path_from_url("sqlite:////tmp/quant.db")

    assert path == Path("/tmp/quant.db")


def test_sqlite_path_from_url_rejects_non_sqlite_url() -> None:
    with pytest.raises(StorageError, match="database_url must start with sqlite:///"):
        sqlite_path_from_url("postgresql://localhost/quant")


def test_open_sqlite_connection_creates_parent_directory_and_uses_row_factory(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'nested' / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        assert connection.row_factory is sqlite3.Row
        connection.execute("create table sample (id integer primary key, name text not null)")
        connection.execute("insert into sample (name) values (?)", ("Quant Stock",))
        row = connection.execute("select name from sample where id = ?", (1,)).fetchone()

    assert row is not None
    assert row["name"] == "Quant Stock"
    assert (tmp_path / "nested" / "quant.db").exists()


def test_open_sqlite_connection_commits_on_context_exit(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        connection.execute("create table sample (id integer primary key, name text not null)")
        connection.execute("insert into sample (name) values (?)", ("committed",))

    with open_sqlite_connection(database_url) as connection:
        row = connection.execute("select name from sample where id = ?", (1,)).fetchone()

    assert row is not None
    assert row["name"] == "committed"
