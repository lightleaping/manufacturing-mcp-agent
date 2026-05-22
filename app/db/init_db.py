from __future__ import annotations

import sqlite3

import pandas as pd

from app.config import (
    PRODUCTION_LOG_PATH,
    QUALITY_LOG_PATH,
    SENSOR_LOG_PATH,
    SQLITE_DB_PATH,
)

SCHEMA_PATH = SQLITE_DB_PATH.parent.parent / "app" / "db" / "schema.sql"


def create_connection() -> sqlite3.Connection:
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(SQLITE_DB_PATH)


def initialize_database() -> None:
    with create_connection() as conn:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema_sql)


def load_csv_to_database() -> None:
    production = pd.read_csv(PRODUCTION_LOG_PATH)
    quality = pd.read_csv(QUALITY_LOG_PATH)
    sensor = pd.read_csv(SENSOR_LOG_PATH)

    with create_connection() as conn:
        production.to_sql("production_logs", conn, if_exists="append", index=False)
        quality.to_sql("quality_inspection", conn, if_exists="append", index=False)
        sensor.to_sql("machine_sensor_logs", conn, if_exists="append", index=False)


def init_db() -> None:
    initialize_database()
    load_csv_to_database()
    print(f"SQLite database initialized: {SQLITE_DB_PATH}")


if __name__ == "__main__":
    init_db()