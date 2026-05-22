# LangFlow Design

## 목적

이 문서는 Manufacturing MCP Agent의 Agent Workflow를 LangFlow 스타일의 시각적 플로우로 표현하기 위한 설계 문서이다.

현재 프로젝트의 실제 실행 Workflow는 LangGraph로 구현되어 있으며, LangFlow는 동일한 흐름을 시각적으로 설계하고 설명하기 위한 구조로 정리했다.

## 전체 흐름

```text
Chat Input
→ Intent Router
→ MCP Tool Selector
→ MCP Tool
→ Evidence Formatter
→ Chat Output
```

## Node 설명

| Node | 역할 |
|---|---|
| Chat Input | 제조 데이터 관련 사용자 질문 입력 |
| Intent Router | 질문을 defect_rate, machine_anomaly, line_performance, quality_issue_candidates로 분류 |
| MCP Tool Selector | intent에 따라 호출할 MCP Tool 선택 |
| defect_rate_by_line | 라인별 불량률 계산 |
| machine_anomalies | 설비 센서 이상 탐지 |
| line_performance | 라인별 생산성 및 품질 요약 |
| quality_issue_candidates | 품질 이상 원인 후보 추정 |
| Evidence Formatter | Tool 결과를 grounded answer 정책에 맞게 정리 |
| Chat Output | answer, intent, tool_name, evidence 반환 |

## LangGraph와의 관계

현재 코드에서는 LangGraph가 아래 단계를 실행한다.

```text
route_question
→ call_tool
→ build_answer
```

LangFlow 설계는 이 구조를 시각화 가능한 형태로 표현한 것이다.

| LangGraph 단계 | LangFlow 설계 Node |
|---|---|
| route_question | Intent Router |
| call_tool | MCP Tool Selector + MCP Tool |
| build_answer | Evidence Formatter + Chat Output |

## MCP Tool Mapping

| intent | MCP Tool |
|---|---|
| defect_rate | defect_rate_by_line |
| machine_anomaly | machine_anomalies |
| line_performance | line_performance |
| quality_issue_candidates | quality_issue_candidates |

## 설계 의도

LangFlow는 Agent Workflow를 시각적으로 설명하기 좋다.  
따라서 이 프로젝트에서는 실제 실행은 LangGraph로 구현하고, LangFlow는 동일한 Agent 흐름을 설계 파일과 문서로 정리했다.

이를 통해 MCP, LangGraph, LangFlow 기반 Agent 구조를 함께 이해하고 있음을 보여준다.

## 향후 확장

- LangFlow UI에서 flow JSON 기반 시각화
- 실제 MCP Client node 연결
- LangChain PromptTemplate node 연결
- LangSmith trace node 또는 callback 연결
- Quality Agent, Equipment Agent, Production Agent로 분리한 A2A workflow 구성
