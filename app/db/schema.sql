DROP TABLE IF EXISTS production_logs;
DROP TABLE IF EXISTS quality_inspection;
DROP TABLE IF EXISTS machine_sensor_logs;

CREATE TABLE production_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    line_id TEXT NOT NULL,
    product_code TEXT NOT NULL,
    output_qty INTEGER NOT NULL,
    operating_hours REAL NOT NULL
);

CREATE TABLE quality_inspection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    line_id TEXT NOT NULL,
    inspected_qty INTEGER NOT NULL,
    defect_qty INTEGER NOT NULL,
    defect_type TEXT NOT NULL
);

CREATE TABLE machine_sensor_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    line_id TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    temperature REAL NOT NULL,
    vibration REAL NOT NULL,
    pressure REAL NOT NULL
);

CREATE INDEX idx_production_date_line
ON production_logs(date, line_id);

CREATE INDEX idx_quality_date_line
ON quality_inspection(date, line_id);

CREATE INDEX idx_sensor_timestamp_line
ON machine_sensor_logs(timestamp, line_id);