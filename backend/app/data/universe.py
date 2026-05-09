from __future__ import annotations

import sqlite3


def get_universe_stock_codes(
    connection: sqlite3.Connection, index_code: str, target_date: str
) -> list[str]:
    from app.data import get_active_stock_codes, get_latest_index_constituents

    latest_codes = get_latest_index_constituents(connection, index_code, target_date)
    active_codes = set(get_active_stock_codes(connection))
    return [code for code in latest_codes if code in active_codes]
