from __future__ import annotations

import sqlite3

import pandas as pd

from app.config import SQLITE_DB_PATH


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(SQLITE_DB_PATH)


def read_sql(query: str, params: tuple = ()) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def get_recent_date_range(table_name: str, date_column: str, days: int) -> tuple[str, str]:
    query = f"""
    SELECT
        DATE(MAX({date_column}), '-' || (? - 1) || ' days') AS start_date,
        MAX({date_column}) AS end_date
    FROM {table_name}
    """
    df = read_sql(query, params=(days,))
    return df.loc[0, "start_date"], df.loc[0, "end_date"]


def load_recent_production_from_db(days: int = 7) -> pd.DataFrame:
    start_date, end_date = get_recent_date_range(
        table_name="production_logs",
        date_column="date",
        days=days,
    )

    query = """
    SELECT *
    FROM production_logs
    WHERE date BETWEEN ? AND ?
    """

    return read_sql(query, params=(start_date, end_date))


def load_recent_quality_from_db(days: int = 7) -> pd.DataFrame:
    start_date, end_date = get_recent_date_range(
        table_name="quality_inspection",
        date_column="date",
        days=days,
    )

    query = """
    SELECT *
    FROM quality_inspection
    WHERE date BETWEEN ? AND ?
    """

    return read_sql(query, params=(start_date, end_date))


def load_recent_sensor_from_db(days: int = 7) -> pd.DataFrame:
    start_date, end_date = get_recent_date_range(
        table_name="machine_sensor_logs",
        date_column="timestamp",
        days=days,
    )

    query = """
    SELECT *
    FROM machine_sensor_logs
    WHERE DATE(timestamp) BETWEEN ? AND ?
    """

    return read_sql(query, params=(start_date, end_date))