from __future__ import annotations

import sqlite3

_DATA_TYPE_DATE_COLUMNS: dict[str, str] = {
    "daily_prices": "trade_date",
    "valuation_metrics": "trade_date",
    "financial_metrics": "report_date",
}


def get_latest_date_by_type(connection: sqlite3.Connection, data_type: str) -> str | None:
    date_column = _DATA_TYPE_DATE_COLUMNS.get(data_type)
    if date_column is None:
        return None

    result = connection.execute(
        f"select max({date_column}) as latest_date from {data_type}",
    ).fetchone()

    return result["latest_date"] if result and result["latest_date"] else None


def get_data_status(connection: sqlite3.Connection) -> dict[str, dict[str, str | bool]]:
    status = {}
    for data_type, _ in _DATA_TYPE_DATE_COLUMNS.items():
        latest_date = get_latest_date_by_type(connection, data_type)
        status[data_type] = {
            "latest_date": latest_date,
            "has_data": latest_date is not None,
        }
    return status
