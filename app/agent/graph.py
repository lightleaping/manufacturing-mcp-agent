from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.mcp_server.tools import (
    detect_machine_anomalies,
    get_defect_rate_by_line,
    infer_quality_issue_candidates_tool,
    summarize_line_performance,
)

from app.agent.prompts import build_answer_prompt


def classify_intent(question: str) -> str:
    """
    사용자 질문을 간단한 규칙으로 분류합니다.
    실제 서비스에서는 LLM 기반 intent classification으로 확장할 수 있습니다.

    분류 우선순위:
    1. 원인/후보/왜 → 품질 이상 원인 후보
    2. 생산성/라인별/요약 → 라인별 생산성 요약
    3. 불량/불량률 → 불량률 분석
    4. 온도/진동/압력/센서/이상 → 설비 센서 이상 탐지
    """
    q = question.lower()

    # 1. 원인 후보 분석: '품질'만으로는 부족하고, 원인/후보/왜가 있어야 함
    if any(keyword in q for keyword in ["원인", "후보", "왜"]):
        if any(keyword in q for keyword in ["불량", "품질", "이상", "defect"]):
            return "quality_issue_candidates"

    # 2. 라인별 생산성/품질 요약
    if any(keyword in q for keyword in ["생산성", "생산량", "라인별", "요약", "performance"]):
        return "line_performance"

    # 3. 불량률 분석
    if any(keyword in q for keyword in ["불량", "defect", "불량률"]):
        return "defect_rate"

    # 4. 설비 센서 이상 탐지
    if any(keyword in q for keyword in ["온도", "진동", "압력", "센서", "이상", "anomaly"]):
        return "machine_anomaly"

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
    summary = result.get("summary", "분석 결과를 생성하지 못했습니다.")

    if not evidence:
        state["answer"] = "현재 데이터에서는 질문에 답하기에 충분한 근거를 찾지 못했습니다."
        return state

    # LangChain PromptTemplate을 사용해 답변 생성 정책을 구조화합니다.
    # 현재 버전은 외부 LLM 호출 없이 Tool summary를 최종 답변으로 사용하고,
    # prompt_text는 향후 LLM 연결 및 LangSmith trace 확장을 위해 생성합니다.
    prompt_text = build_answer_prompt(
        question=state["question"],
        intent=state["intent"],
        tool_name=state["tool_name"],
        summary=summary,
        evidence=evidence,
    )

    state["answer"] = summary
    state["tool_result"]["prompt_text"] = prompt_text

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