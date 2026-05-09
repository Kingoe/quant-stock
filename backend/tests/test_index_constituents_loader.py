import pytest

from app.data import (
    IndexConstituentRecord,
    get_index_constituents,
    get_latest_index_constituents,
    load_index_constituents,
)
from app.storage import initialize_schema, open_sqlite_connection


def test_load_index_constituents_inserts_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("CSI800", "600000", "2026-05-08", 0.0123),
                IndexConstituentRecord("CSI800", "000001", "2026-05-08", 0.0101),
            ],
        )

        stock_codes = get_index_constituents(connection, "CSI800", "2026-05-08")

    assert stock_codes == ["000001", "600000"]


def test_load_index_constituents_updates_existing_weight(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_index_constituents(
            connection,
            [IndexConstituentRecord("CSI800", "600000", "2026-05-08", 0.0123)],
        )
        load_index_constituents(
            connection,
            [IndexConstituentRecord("CSI800", "600000", "2026-05-08", 0.0234)],
        )

        row = connection.execute(
            """
            select weight
            from index_constituents
            where index_code = ? and stock_code = ? and trade_date = ?
            """,
            ("CSI800", "600000", "2026-05-08"),
        ).fetchone()

    assert row["weight"] == 0.0234


def test_get_index_constituents_is_scoped_by_index_code_and_trade_date(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("CSI800", "600000", "2026-05-08", 0.0123),
                IndexConstituentRecord("CSI300", "000001", "2026-05-08", 0.0200),
                IndexConstituentRecord("CSI800", "300750", "2026-05-09", 0.0180),
            ],
        )

        stock_codes = get_index_constituents(connection, "CSI800", "2026-05-08")

    assert stock_codes == ["600000"]


def test_get_latest_index_constituents_uses_latest_available_date_on_or_before_target(
    tmp_path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        load_index_constituents(
            connection,
            [
                IndexConstituentRecord("CSI800", "600000", "2026-05-06", 0.0123),
                IndexConstituentRecord("CSI800", "000001", "2026-05-08", 0.0101),
                IndexConstituentRecord("CSI800", "300750", "2026-05-08", 0.0180),
                IndexConstituentRecord("CSI800", "688001", "2026-05-12", 0.0080),
            ],
        )

        stock_codes = get_latest_index_constituents(connection, "CSI800", "2026-05-11")

    assert stock_codes == ["000001", "300750"]


def test_load_index_constituents_rejects_empty_records(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant.db'}"

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)

        with pytest.raises(ValueError, match="records must not be empty"):
            load_index_constituents(connection, [])
