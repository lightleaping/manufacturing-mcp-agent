from __future__ import annotations

from app.services.quality_analyzer import (
    analyze_defect_rate_by_line,
    summarize_performance_by_line,
    infer_quality_issue_candidates,
)
from app.services.anomaly_detector import find_sensor_anomalies


def get_defect_rate_by_line(days: int = 7) -> dict:
    """
    MCP Tool: 라인별 불량률을 계산하고 불량률이 높은 라인을 반환합니다.
    """
    return analyze_defect_rate_by_line(days=days)


def detect_machine_anomalies(days: int = 7) -> dict:
    """
    MCP Tool: 설비 센서 로그에서 임계값 기반 이상 구간을 탐지합니다.
    """
    return find_sensor_anomalies(days=days)


def summarize_line_performance(days: int = 7) -> dict:
    """
    MCP Tool: 라인별 생산량, 불량률, 생산성을 요약합니다.
    """
    return summarize_performance_by_line(days=days)


def infer_quality_issue_candidates_tool(days: int = 7) -> dict:
    """
    MCP Tool: 불량률과 센서 이상 정보를 함께 보고 품질 이상 원인 후보를 추정합니다.
    """
    return infer_quality_issue_candidates(days=days)