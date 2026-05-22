from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PRODUCTION_LOG_PATH = DATA_DIR / "production_logs.csv"
QUALITY_LOG_PATH = DATA_DIR / "quality_inspection.csv"
SENSOR_LOG_PATH = DATA_DIR / "machine_sensor_logs.csv"

DEFAULT_DAYS = 7

SQLITE_DB_PATH = DATA_DIR / "manufacturing.db"