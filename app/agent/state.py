from typing import Any, TypedDict


class AgentState(TypedDict):
    question: str
    intent: str
    tool_name: str
    tool_result: dict[str, Any]
    answer: str
    evidence: list[dict]