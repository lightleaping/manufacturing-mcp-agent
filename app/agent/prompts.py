from __future__ import annotations

from langchain_core.prompts import PromptTemplate


GROUNDED_ANSWER_POLICY = """
당신은 제조 데이터 진단 AI Agent입니다.

답변 규칙:
1. Tool 결과에 포함된 evidence를 근거로만 답변합니다.
2. evidence에 없는 수치나 원인은 추측하지 않습니다.
3. 품질 이상 원인은 확정하지 않고 '원인 후보', '우선 점검 대상'으로 표현합니다.
4. 데이터가 부족하면 추가 데이터가 필요하다고 명시합니다.
5. 답변에는 핵심 지표와 근거를 함께 포함합니다.
"""


ANSWER_PROMPT = PromptTemplate.from_template(
    """
{policy}

사용자 질문:
{question}

분류된 intent:
{intent}

호출된 tool:
{tool_name}

Tool 요약:
{summary}

근거 데이터:
{evidence}

위 정보를 바탕으로 사용자에게 제공할 답변을 작성하세요.
"""
)


def build_answer_prompt(
    question: str,
    intent: str,
    tool_name: str,
    summary: str,
    evidence: list[dict],
) -> str:
    return ANSWER_PROMPT.format(
        policy=GROUNDED_ANSWER_POLICY,
        question=question,
        intent=intent,
        tool_name=tool_name,
        summary=summary,
        evidence=evidence,
    )