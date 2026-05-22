from app.mcp_server.tools import (
    detect_machine_anomalies,
    get_defect_rate_by_line,
    infer_quality_issue_candidates_tool,
    summarize_line_performance,
)


def test_defect_rate_tool_returns_evidence():
    result = get_defect_rate_by_line(days=7)

    assert "summary" in result
    assert "evidence" in result
    assert len(result["evidence"]) > 0
    assert result["evidence"][0]["line_id"] == "LINE_C"


def test_anomaly_tool_returns_summary():
    result = detect_machine_anomalies(days=7)

    assert "summary" in result
    assert "evidence" in result
    assert "센서 이상" in result["summary"]


def test_performance_tool_returns_evidence():
    result = summarize_line_performance(days=7)

    assert "summary" in result
    assert "evidence" in result
    assert len(result["evidence"]) > 0


def test_quality_issue_candidates_returns_line_c():
    result = infer_quality_issue_candidates_tool(days=7)

    assert "summary" in result
    assert "evidence" in result
    assert len(result["evidence"]) > 0
    assert result["evidence"][0]["line_id"] == "LINE_C"