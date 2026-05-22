from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.mcp_server.tools import (
    detect_machine_anomalies,
    get_defect_rate_by_line,
    infer_quality_issue_candidates_tool,
    summarize_line_performance,
)


def classify_intent(question: str) -> str:
    """
    사용자 질문을 간단한 규칙으로 분류합니다.
    실제 서비스에서는 LLM 기반 intent classification으로 확장할 수 있습니다.

    분류 우선순위:
    1. 품질 이상 원인 후보
    2. 불량률 분석
    3. 설비 센서 이상 탐지
    4. 라인별 생산성 요약
    """
    q = question.lower()

    # 1. 품질 이상 원인 후보 질문은 '이상'보다 '원인/후보/품질'을 우선 판단
    if any(keyword in q for keyword in ["원인", "후보", "왜", "품질"]):
        if any(keyword in q for keyword in ["불량", "품질", "이상", "defect"]):
            return "quality_issue_candidates"

    # 2. 불량률 분석
    if any(keyword in q for keyword in ["불량", "defect", "불량률"]):
        return "defect_rate"

    # 3. 설비 센서 이상 탐지
    if any(keyword in q for keyword in ["온도", "진동", "압력", "센서", "anomaly"]):
        return "machine_anomaly"

    # 4. 라인별 생산성 요약
    if any(keyword in q for keyword in ["생산성", "생산량", "라인별", "요약", "performance"]):
        return "line_performance"

    return "line_performance"

def route_question(state: AgentState) -> AgentState:
    intent = classify_intent(state["question"])
    state["intent"] = intent

    tool_map = {
        "defect_rate": "get_defect_rate_by_line",
        "machine_anomaly": "detect_machine_anomalies",
        "line_performance": "summarize_line_performance",
        "quality_issue_candidates": "infer_quality_issue_candidates_tool",
    }

    state["tool_name"] = tool_map[intent]
    return state


def call_tool(state: AgentState) -> AgentState:
    tool_name = state["tool_name"]

    if tool_name == "get_defect_rate_by_line":
        result = get_defect_rate_by_line(days=7)
    elif tool_name == "detect_machine_anomalies":
        result = detect_machine_anomalies(days=7)
    elif tool_name == "summarize_line_performance":
        result = summarize_line_performance(days=7)
    elif tool_name == "infer_quality_issue_candidates_tool":
        result = infer_quality_issue_candidates_tool(days=7)
    else:
        result = {
            "summary": "지원하지 않는 질문 유형입니다.",
            "evidence": [],
        }

    state["tool_result"] = result
    state["evidence"] = result.get("evidence", [])
    return state


def build_answer(state: AgentState) -> AgentState:
    result = state["tool_result"]
    evidence = result.get("evidence", [])

    if not evidence:
        state["answer"] = "현재 데이터에서는 질문에 답하기에 충분한 근거를 찾지 못했습니다."
        return state

    state["answer"] = result.get("summary", "분석 결과를 생성하지 못했습니다.")
    return state


def create_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("route_question", route_question)
    workflow.add_node("call_tool", call_tool)
    workflow.add_node("build_answer", build_answer)

    workflow.set_entry_point("route_question")
    workflow.add_edge("route_question", "call_tool")
    workflow.add_edge("call_tool", "build_answer")
    workflow.add_edge("build_answer", END)

    return workflow.compile()


_graph = create_graph()


def run_agent(question: str) -> dict:
    initial_state: AgentState = {
        "question": question,
        "intent": "",
        "tool_name": "",
        "tool_result": {},
        "answer": "",
        "evidence": [],
    }

    final_state = _graph.invoke(initial_state)

    return {
        "question": final_state["question"],
        "intent": final_state["intent"],
        "tool_name": final_state["tool_name"],
        "answer": final_state["answer"],
        "evidence": final_state["evidence"],
    }