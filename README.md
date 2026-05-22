# Manufacturing MCP Agent

제조 데이터 탐색·진단을 위한 MCP 기반 AI Agent 시스템입니다.

사용자가 제조 현장 데이터에 대해 자연어로 질문하면, Agent가 질문 유형을 판단하고 필요한 MCP Tool을 호출하여 생산 로그, 품질 검사, 설비 센서 데이터를 분석한 뒤 근거 기반 답변을 반환합니다.

이 프로젝트는 인터엑스 AI Agent Engineer 포지션의 요구 기술인 MCP, LangGraph, LangChain, LangFlow, FastAPI, SQL/DB, PyTorch, Docker, CI/CD, Agent trace logging을 포트폴리오 프로젝트 안에서 최대한 반영하기 위해 진행했습니다.

---

## 1. 프로젝트 개요

이 프로젝트는 제조 현장의 생산·품질·설비 데이터를 대상으로 동작하는 AI Agent 백엔드 예제입니다.

단순히 질문에 답하는 챗봇이 아니라, 사용자의 질문을 분석한 뒤 필요한 Tool을 선택하고, 실제 데이터 분석 결과를 근거로 답변을 생성하는 구조를 목표로 했습니다.

구현 범위는 다음과 같습니다.

- 제조 샘플 데이터 생성
- CSV 기반 데이터 분석
- SQLite DB 적재 및 SQL 조회
- MCP Tool 구조
- MCP Server entrypoint
- LangGraph Agent Workflow
- LangChain PromptTemplate 기반 답변 정책
- FastAPI Agent API
- PyTorch SensorAutoEncoder 모델 서빙
- Agent trace logging
- Docker 실행 환경
- pytest 자동 테스트
- GitHub Actions CI
- LangFlow 스타일 Workflow 설계 문서 및 flow JSON

---

## 2. 주요 기능

### 2-1. 라인별 불량률 분석

사용자 질문 예시:

```text
최근 7일간 불량률이 가장 높은 라인을 찾아줘.
```

응답 예시:

```text
최근 7일 기준 불량률이 가장 높은 라인은 LINE_C입니다.
평균 불량률은 4.39%, 총 생산량은 7677개, 총 불량 수량은 340개입니다.
```

### 2-2. 설비 센서 이상 탐지

사용자 질문 예시:

```text
설비 온도나 진동이 비정상적으로 높은 구간이 있어?
```

응답 예시:

```text
최근 7일 기준 센서 이상은 총 9건 발견되었습니다.
가장 많이 발생한 라인은 LINE_C이며 9건입니다.
```

### 2-3. 라인별 생산성 및 품질 요약

사용자 질문 예시:

```text
라인별 생산성과 품질 상태를 요약해줘.
```

응답 예시:

```text
최근 7일 기준 생산성이 가장 높은 라인은 LINE_D이며,
품질 측면에서는 LINE_C의 평균 불량률이 가장 높습니다.
```

### 2-4. 품질 이상 원인 후보 추정

사용자 질문 예시:

```text
품질 이상 원인 후보를 데이터 근거와 함께 알려줘.
```

응답 예시:

```text
LINE_C에서 평균 불량률, 최대 온도, 최대 진동이 함께 높게 관찰되었습니다.
따라서 해당 라인의 설비 조건을 우선 점검할 필요가 있습니다.
단, 이 결과는 샘플 데이터 기반의 규칙 분석이므로 실제 원인 확정에는 추가 현장 데이터가 필요합니다.
```

### 2-5. PyTorch 센서 이상탐지 모델 서빙

FastAPI의 `/model/sensor-anomaly` endpoint를 통해 센서 입력값에 대한 anomaly score를 반환합니다.

요청 예시:

```json
{
  "temperature": 95.7,
  "vibration": 5.6,
  "pressure": 2.4
}
```

응답 예시:

```json
{
  "temperature": 95.7,
  "vibration": 5.6,
  "pressure": 2.4,
  "anomaly_score": 2573.63623046875,
  "threshold": 1000,
  "is_anomaly": true,
  "model": "SensorAutoEncoder",
  "note": "현재 모델은 포트폴리오용 기본 AutoEncoder 구조입니다. 실제 운영에서는 정상 센서 데이터로 학습한 weight와 검증 기반 threshold가 필요합니다."
}
```

현재 모델은 포트폴리오용 기본 AutoEncoder 구조입니다. 실제 운영에서는 정상 센서 데이터 기반 학습 weight와 검증 기반 threshold 산정이 필요합니다.

---

## 3. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python |
| API Server | FastAPI, Uvicorn |
| Agent Workflow | LangGraph |
| Prompt Policy | LangChain PromptTemplate |
| Tool Interface | MCP, FastMCP |
| Visual Workflow Design | LangFlow-style Flow JSON |
| Data Processing | pandas |
| DB / SQL | SQLite, SQL schema, CSV-to-DB pipeline |
| Model Serving | PyTorch SensorAutoEncoder, FastAPI model endpoint |
| Observability | Agent trace logging, JSONL |
| Test | pytest |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## 4. 시스템 구조

```text
User Question
  ↓
FastAPI /agent/query
  ↓
LangGraph Agent Workflow
  ↓
Question Intent Routing
  ↓
MCP Tool Selection
  ↓
Manufacturing Data Analysis
  ↓
Evidence-based Answer
```

모델 서빙 구조는 별도 endpoint로 구성했습니다.

```text
Sensor Input
  ↓
FastAPI /model/sensor-anomaly
  ↓
PyTorch SensorAutoEncoder
  ↓
Anomaly Score
  ↓
Prediction Result
```

---

## 5. 데이터 구성

이 프로젝트는 실제 제조 데이터를 사용할 수 없기 때문에 샘플 데이터를 생성해 사용합니다.

| 파일 | 설명 |
|---|---|
| data/production_logs.csv | 라인별 생산량, 제품 코드, 가동 시간 |
| data/quality_inspection.csv | 라인별 검사 수량, 불량 수량, 불량 유형 |
| data/machine_sensor_logs.csv | 설비별 온도, 진동, 압력 센서 로그 |

샘플 데이터는 `scripts_generate_sample_data.py`로 생성합니다.

```bash
python scripts_generate_sample_data.py
```

### SQLite DB Pipeline

샘플 CSV 데이터는 SQLite DB로 적재할 수 있도록 구성했습니다.

```bash
python -m app.db.init_db
```

DB 테이블:

| 테이블 | 설명 |
|---|---|
| production_logs | 생산 로그 |
| quality_inspection | 품질 검사 로그 |
| machine_sensor_logs | 설비 센서 로그 |

이를 통해 CSV 기반 분석뿐 아니라 SQL 기반 데이터 조회 구조도 함께 구성했습니다.

---

## 6. Agent Workflow

LangGraph를 사용하여 Agent 동작을 단계별로 구성했습니다.

```text
route_question
→ call_tool
→ build_answer
```

### route_question

사용자 질문을 분석해 intent를 분류합니다.

| intent | 설명 | 연결 Tool |
|---|---|---|
| defect_rate | 불량률 분석 | get_defect_rate_by_line |
| machine_anomaly | 설비 이상 탐지 | detect_machine_anomalies |
| line_performance | 라인별 성능 요약 | summarize_line_performance |
| quality_issue_candidates | 품질 이상 원인 후보 | infer_quality_issue_candidates_tool |

### call_tool

분류된 intent에 따라 MCP Tool 형태의 분석 함수를 호출합니다.

### build_answer

Tool 결과의 summary와 evidence를 기반으로 최종 응답을 구성합니다.

### LangChain Prompt Policy

`app/agent/prompts.py`에서 LangChain `PromptTemplate`을 사용해 grounded answer 정책을 분리했습니다.

답변 정책:

- Tool 결과에 포함된 evidence를 근거로만 답변
- evidence에 없는 수치나 원인 추측 금지
- 품질 이상 원인은 확정하지 않고 원인 후보 또는 우선 점검 대상으로 표현
- 데이터가 부족하면 추가 데이터 필요성을 명시
- 핵심 지표와 근거를 함께 포함

현재 버전은 외부 LLM API를 호출하지 않고 Tool summary를 최종 답변으로 사용합니다. 다만 PromptTemplate으로 답변 정책과 입력 정보를 구조화해, 향후 LLM 모델 또는 LangSmith trace 연동이 가능하도록 설계했습니다.

---

## 7. MCP Server 구성

제조 데이터 분석 기능을 MCP Tool로 분리했습니다.

| MCP Tool | 역할 |
|---|---|
| defect_rate_by_line | 라인별 불량률 계산 |
| machine_anomalies | 설비 센서 이상 탐지 |
| line_performance | 라인별 생산성 및 품질 요약 |
| quality_issue_candidates | 품질 이상 원인 후보 추정 |

MCP Server 실행:

```bash
python -m app.mcp_server.server
```

MCP Server는 stdio 기반 MCP Client 연결을 전제로 실행됩니다.  
명령 실행 후 터미널이 대기 상태가 되면 정상이며, 직접 실행 상태에서 `Ctrl + C`로 종료하면 `KeyboardInterrupt` 로그가 출력될 수 있습니다.

---

## 8. LangFlow Design

실제 Agent 실행은 LangGraph로 구현했으며, 동일한 Workflow를 LangFlow 스타일의 flow JSON과 설계 문서로 정리했습니다.

| 파일 | 설명 |
|---|---|
| docs/langflow_design.md | LangFlow 스타일 설계 문서 |
| langflow/manufacturing_agent_flow.json | Agent workflow flow JSON |

흐름:

```text
Chat Input
→ Intent Router
→ MCP Tool Selector
→ MCP Tool
→ Evidence Formatter
→ Chat Output
```

이 구조는 LangGraph의 `route_question → call_tool → build_answer` 흐름을 시각화 가능한 형태로 표현한 것입니다.

---

## 9. Agent Trace Logging

Agent 실행 시 아래 정보를 JSONL 로그로 저장합니다.

| 필드 | 설명 |
|---|---|
| created_at | 실행 시각 |
| question | 사용자 질문 |
| intent | 분류된 질문 의도 |
| tool_name | 호출된 Tool |
| evidence_count | 반환된 근거 개수 |
| status | 실행 상태 |

로그 파일:

```text
logs/agent_trace.jsonl
```

로그 파일은 실행 중 생성되며 Git에는 포함하지 않습니다.

이 구조는 향후 LangSmith, OpenTelemetry, LLMOps Dashboard로 확장 가능한 최소 trace 구조입니다.

---

## 10. FastAPI 실행 방법

### 10-1. 가상환경 생성

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 10-2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 10-3. 샘플 데이터 생성

```bash
python scripts_generate_sample_data.py
```

### 10-4. SQLite DB 초기화

```bash
python -m app.db.init_db
```

### 10-5. 서버 실행

```bash
uvicorn app.main:app --reload
```

Swagger 문서:

```text
http://127.0.0.1:8000/docs
```

---

## 11. API 사용 예시

### 11-1. Agent Query API

Endpoint:

```text
POST /agent/query
```

Request:

```json
{
  "question": "최근 7일간 불량률이 가장 높은 라인을 찾아줘."
}
```

Response:

```json
{
  "question": "최근 7일간 불량률이 가장 높은 라인을 찾아줘.",
  "intent": "defect_rate",
  "tool_name": "get_defect_rate_by_line",
  "answer": "최근 7일 기준 불량률이 가장 높은 라인은 LINE_C입니다. 평균 불량률은 4.39%, 총 생산량은 7677개, 총 불량 수량은 340개입니다.",
  "evidence": [
    {
      "line_id": "LINE_C",
      "output_qty": 7677,
      "inspected_qty": 6562,
      "defect_qty": 340,
      "avg_defect_rate": 0.04394263227427786,
      "max_defect_rate": 0.052587646076794656
    }
  ]
}
```

### 11-2. PyTorch Model Serving API

Endpoint:

```text
POST /model/sensor-anomaly
```

Request:

```json
{
  "temperature": 95.7,
  "vibration": 5.6,
  "pressure": 2.4
}
```

Response:

```json
{
  "temperature": 95.7,
  "vibration": 5.6,
  "pressure": 2.4,
  "anomaly_score": 2573.63623046875,
  "threshold": 1000,
  "is_anomaly": true,
  "model": "SensorAutoEncoder",
  "note": "현재 모델은 포트폴리오용 기본 AutoEncoder 구조입니다. 실제 운영에서는 정상 센서 데이터로 학습한 weight와 검증 기반 threshold가 필요합니다."
}
```

---

## 12. Docker 실행

Docker Desktop 실행 후 아래 명령어를 사용합니다.

```bash
docker compose up --build
```

브라우저에서 확인:

```text
http://127.0.0.1:8000/docs
```

종료:

```bash
docker compose down
```

---

## 13. 테스트

```bash
pytest
```

또는:

```bash
python -m pytest
```

현재 테스트 항목:

- 불량률 분석 Tool 테스트
- 설비 이상 탐지 Tool 테스트
- 라인별 생산성 요약 Tool 테스트
- 품질 이상 원인 후보 Tool 테스트
- Agent intent routing 테스트
- PyTorch SensorAutoEncoder 모델 서빙 테스트

테스트 결과:

```text
9 passed
```

---

## 14. CI/CD

GitHub Actions를 통해 push 또는 pull request 시 자동 테스트를 실행하도록 구성했습니다.

Workflow 파일:

```text
.github/workflows/ci.yml
```

CI 단계:

```text
Checkout repository
→ Set up Python
→ Install dependencies
→ Generate sample manufacturing data
→ Initialize SQLite database
→ Run tests
```

---

## 15. 문제 해결 및 개선 과정

### 15-1. Agent 라우팅 우선순위 개선

초기 Agent 라우팅 규칙에서는 `품질 이상 원인 후보` 질문이 `이상` 키워드 때문에 설비 이상 탐지 Tool로 잘못 연결되는 문제가 있었습니다.

이를 해결하기 위해 `원인`, `후보`, `왜`와 같은 목적 단어가 있을 때만 품질 이상 원인 후보 Tool로 라우팅되도록 규칙 우선순위를 조정했습니다.

### 15-2. Docker requirements 최소화

초기 `requirements.txt`는 로컬 Windows 가상환경 전체를 freeze한 결과라 Docker Linux 환경에서 `pywin32` 설치 오류가 발생했습니다.

이를 해결하기 위해 실제 서비스 실행에 필요한 패키지만 남기고 requirements를 최소화했습니다.

### 15-3. Docker Engine 및 빌드 이슈 해결

Docker Desktop이 실행되지 않은 상태에서는 Docker daemon 연결 오류가 발생했습니다.  
Docker Desktop 실행 후 Docker Engine 연결을 확인하고, `docker compose up --build`로 이미지 빌드와 컨테이너 실행을 검증했습니다.

---

## 16. 한계와 개선 방향

현재 프로젝트는 포트폴리오용 미니 프로젝트이므로 실제 제조 현장 데이터가 아닌 샘플 데이터를 사용합니다.

또한 PyTorch 모델은 실제 학습 weight를 사용하지 않는 기본 AutoEncoder 구조이며, 운영 환경에서는 정상 센서 데이터 기반 학습과 검증 기반 threshold 산정이 필요합니다.

향후 개선 방향은 다음과 같습니다.

- PostgreSQL 기반 운영 DB 전환
- Redis 기반 자주 조회되는 라인별 지표 캐싱
- Kafka 기반 실시간 센서 데이터 스트리밍
- LangSmith 기반 Agent trace 및 tool call 관측
- A2A 구조로 품질 Agent, 설비 Agent, 생산 Agent 분리
- PyTorch 기반 시계열 이상탐지 모델 학습 및 weight 서빙
- LangFlow UI에서 실제 flow 시각화
- 실제 MCP Client와 연동해 외부 도구 호출 구조 강화
- Cloud Run, AWS ECS 등 컨테이너 배포 환경 적용

---

## 17. 포트폴리오 요약

이 프로젝트에서는 제조 데이터를 대상으로 MCP Tool과 LangGraph 기반 Agent Workflow를 구성했습니다.

사용자의 자연어 질문을 intent로 분류하고, 필요한 Tool을 호출하여 생산 로그, 품질 검사, 설비 센서 데이터를 분석한 뒤 answer와 evidence를 함께 반환하도록 구현했습니다.

또한 SQLite 기반 DB Pipeline, LangChain PromptTemplate 기반 답변 정책, PyTorch SensorAutoEncoder 모델 서빙, Agent trace logging, Docker 실행 환경, GitHub Actions CI, LangFlow-style flow 설계 문서를 추가하여 단순 데모가 아니라 실행·검증·관측·확장 흐름을 갖춘 AI Agent 백엔드 프로젝트로 정리했습니다.
