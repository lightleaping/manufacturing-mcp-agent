from __future__ import annotations

import pandas as pd

from app.config import PRODUCTION_LOG_PATH, QUALITY_LOG_PATH, SENSOR_LOG_PATH


def load_production_logs() -> pd.DataFrame:
    """생산 로그 CSV를 읽어 DataFrame으로 반환합니다."""
    return pd.read_csv(PRODUCTION_LOG_PATH, parse_dates=["date"])


def load_quality_logs() -> pd.DataFrame:
    """품질 검사 CSV를 읽어 DataFrame으로 반환합니다."""
    return pd.read_csv(QUALITY_LOG_PATH, parse_dates=["date"])


def load_sensor_logs() -> pd.DataFrame:
    """설비 센서 CSV를 읽어 DataFrame으로 반환합니다."""
    return pd.read_csv(SENSOR_LOG_PATH, parse_dates=["timestamp"])


def filter_recent_by_date(
    df: pd.DataFrame,
    date_col: str,
    days: int,
) -> pd.DataFrame:
    """가장 최근 날짜 기준으로 N일치 데이터만 필터링합니다."""
    max_date = df[date_col].max()
    min_date = max_date - pd.Timedelta(days=days - 1)

    return df[
        (df[date_col] >= min_date)
        & (df[date_col] <= max_date)
    ].copy()