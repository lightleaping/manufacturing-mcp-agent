from app.agent.graph import run_agent


def test_agent_routes_defect_question():
    result = run_agent("최근 7일간 불량률이 가장 높은 라인을 찾아줘.")

    assert result["intent"] == "defect_rate"
    assert result["tool_name"] == "get_defect_rate_by_line"
    assert "LINE_C" in result["answer"]
    assert len(result["evidence"]) > 0


def test_agent_routes_anomaly_question():
    result = run_agent("설비 온도나 진동이 비정상적으로 높은 구간이 있어?")

    assert result["intent"] == "machine_anomaly"
    assert result["tool_name"] == "detect_machine_anomalies"
    assert len(result["evidence"]) > 0


def test_agent_routes_performance_question():
    result = run_agent("라인별 생산성과 품질 상태를 요약해줘.")

    assert result["intent"] == "line_performance"
    assert result["tool_name"] == "summarize_line_performance"
    assert len(result["evidence"]) > 0


def test_agent_routes_quality_candidate_question():
    result = run_agent("품질 이상 원인 후보를 데이터 근거와 함께 알려줘.")

    assert result["intent"] == "quality_issue_candidates"
    assert result["tool_name"] == "infer_quality_issue_candidates_tool"
    assert "LINE_C" in result["answer"]
    assert len(result["evidence"]) > 0