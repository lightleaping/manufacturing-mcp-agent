from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from app.mcp_server.tools import (
    detect_machine_anomalies,
    get_defect_rate_by_line,
    infer_quality_issue_candidates_tool,
    summarize_line_performance,
)


mcp = FastMCP("manufacturing-mcp-agent")


@mcp.tool()
def defect_rate_by_line(days: int = 7) -> dict:
    """
    라인별 불량률을 계산하고 평균 불량률이 높은 라인을 반환합니다.
    """
    return get_defect_rate_by_line(days=days)


@mcp.tool()
def machine_anomalies(days: int = 7) -> dict:
    """
    설비 센서 로그에서 온도, 진동, 압력 임계값을 초과한 이상 구간을 탐지합니다.
    """
    return detect_machine_anomalies(days=days)


@mcp.tool()
def line_performance(days: int = 7) -> dict:
    """
    라인별 생산량, 가동시간, 생산성, 불량률을 요약합니다.
    """
    return summarize_line_performance(days=days)


@mcp.tool()
def quality_issue_candidates(days: int = 7) -> dict:
    """
    불량률과 센서 이상 데이터를 함께 분석해 품질 이상 원인 후보를 추정합니다.
    """
    return infer_quality_issue_candidates_tool(days=days)


if __name__ == "__main__":
    mcp.run()