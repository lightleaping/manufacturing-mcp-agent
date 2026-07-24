# Manufacturing MCP Agent

제조 현장의 생산 로그, 품질 검사 로그, 설비 센서 로그를 기반으로 자연어 질의를 처리하는 FastAPI 기반 제조 분석 Agent 프로젝트입니다. 사용자의 입력은 LangGraph workflow를 통해 intent로 분류되고, intent에 맞는 MCP-style Tool 함수가 실행됩니다. 각 Tool은 분석 결과 `summary`와 근거 데이터 `evidence`를 반환합니다.

## 1. 프로젝트 개요

이 프로젝트는 제조 데이터 분석 흐름을 Agent 구조로 구성한 백엔드입니다. 단순히 하나의 분석 함수를 호출하는 구조가 아니라, 입력 문장을 분류하고, 해당 의도에 맞는 Tool을 선택하고, Tool 결과를 근거 기반 응답으로 정리하는 흐름을 갖습니다.

핵심 흐름은 다음과 같습니다.

```text
사용자 입력
→ FastAPI /agent/query
→ run_agent()
→ LangGraph workflow
→ route_question()
→ call_tool()
→ MCP-style Tool 함수
→ summary / evidence
→ build_answer()
→ API 응답
```

별도로 `/model/sensor-anomaly` endpoint는 `temperature`, `vibration`, `pressure` 값을 직접 입력받아 PyTorch AutoEncoder 기반 `anomaly_score`와 `is_anomaly`를 반환합니다. 이 모델 endpoint는 현재 Agent Tool 흐름과 분리되어 있습니다.

## 2. 주요 기능

- 라인별 불량률 분석
- 설비 센서 이상 구간 탐지
- 라인별 생산성 및 품질 상태 요약
- 불량률과 센서 지표 기반 품질 이상 원인 후보 추론
- PyTorch AutoEncoder 기반 센서 anomaly score 계산 endpoint
- pytest 기반 Agent flow, Tool, 모델 service 검증
- Docker 기반 실행 환경 구성
- GitHub Actions CI 기반 자동 테스트

## 3. 기술 스택

| 구분 | 사용 기술 | 역할 |
|---|---|---|
| API | FastAPI, Pydantic | endpoint 정의, 요청/응답 schema 검증 |
| Agent Workflow | LangGraph | route_question → call_tool → build_answer 흐름 구성 |
| Tool Layer | Python functions, FastMCP 확장 기반 | Agent가 호출할 수 있는 제조 분석 기능 단위 |
| Data Processing | pandas | CSV 로딩, 병합, 집계, 최근 N일 필터링 |
| Model Serving | PyTorch | SensorAutoEncoder 기반 reconstruction error 계산 |
| Test | pytest | Agent, Tool, 모델 service 검증 |
| Infra | Docker, GitHub Actions | 실행 환경 재현, 자동 테스트 |
| Storage 준비 | SQLite | schema, CSV 적재, 조회 helper 준비 |

## 4. API Endpoints

### POST `/agent/query`

제조 데이터 관련 자연어 입력을 받아 Agent workflow를 실행합니다.

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
  "answer": "최근 7일 기준 불량률이 가장 높은 라인은 LINE_C입니다...",
  "evidence": [
    {
      "line_id": "LINE_C",
      "output_qty": 1234,
      "defect_qty": 54,
      "avg_defect_rate": 0.0439
    }
  ]
}
```

### POST `/model/sensor-anomaly`

센서값 3개를 직접 입력받아 AutoEncoder 기반 anomaly score를 계산합니다.

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
  "anomaly_score": 1023.5,
  "threshold": 1000.0,
  "is_anomaly": true,
  "model": "SensorAutoEncoder",
  "note": "현재 모델은 포트폴리오용 기본 AutoEncoder 구조입니다..."
}
```

## 5. Agent Workflow

Agent workflow는 `route_question`, `call_tool`, `build_answer` 세 node로 구성됩니다.

```text
route_question
→ 입력 문장을 intent로 분류하고 tool_name 결정

call_tool
→ tool_name에 맞는 Tool 함수 호출
→ tool_result, evidence 저장

build_answer
→ Tool 결과의 summary/evidence를 최종 answer로 정리
```

현재 workflow는 단순 선형 구조입니다. 일반 함수 호출로도 구현할 수 있지만, LangGraph를 사용하면 Agent 처리 단계를 node 단위로 분리하고, `AgentState`가 각 단계에서 어떻게 채워지는지 명확하게 표현할 수 있습니다. 향후 unknown intent 분기, evidence 검증, LLM 답변 생성, 오류 처리 node를 추가하기 쉽습니다.

## 6. AgentState

`AgentState`는 LangGraph workflow 안에서 각 node가 공유하는 상태 객체입니다. 처음에는 `question`만 의미 있게 들어오고, node를 지나면서 `intent`, `tool_name`, `tool_result`, `answer`, `evidence`가 채워집니다.

```text
initial_state
question만 포함

route_question 이후
question + intent + tool_name

call_tool 이후
question + intent + tool_name + tool_result + evidence

build_answer 이후
question + intent + tool_name + tool_result + evidence + answer
```

## 7. Intent와 Tool 매핑

| intent | tool_name | 실행 Tool | 설명 |
|---|---|---|---|
| `defect_rate` | `get_defect_rate_by_line` | `analyze_defect_rate_by_line()` | 최근 N일 라인별 불량률 분석 |
| `machine_anomaly` | `detect_machine_anomalies` | `find_sensor_anomalies()` | 온도·진동·압력 기준 센서 이상 탐지 |
| `line_performance` | `summarize_line_performance` | `summarize_performance_by_line()` | 라인별 생산성과 품질 상태 요약 |
| `quality_issue_candidates` | `infer_quality_issue_candidates_tool` | `infer_quality_issue_candidates()` | 불량률과 센서 지표 기반 우선 점검 후보 추론 |

현재 intent classification은 LLM 기반이 아니라 규칙 기반입니다. 입력 문자열에 포함된 키워드를 기준으로 intent를 분류합니다.

## 8. Tool Layer

`tools.py`는 실제 분석을 직접 수행하기보다 Agent가 호출할 수 있는 Tool 입구를 제공합니다. 실제 계산은 `quality_analyzer.py`와 `anomaly_detector.py`의 service 함수에 위임합니다.

```text
graph.py
→ Agent workflow 제어

tools.py
→ Agent가 호출할 수 있는 Tool 입구

quality_analyzer.py / anomaly_detector.py
→ 실제 데이터 분석 계산
```

이 프로젝트의 Tool layer는 MCP 개념을 참고해 분석 기능을 Tool 단위로 분리한 구조입니다. 다만 현재 `/agent/query` 핵심 흐름은 MCP client가 protocol로 Tool을 호출하는 방식이 아니라, Python 코드 내부에서 Tool 함수를 직접 호출합니다. 따라서 구현 수준은 완전한 MCP protocol server라기보다 MCP-style Tool layer에 가깝습니다.

## 9. 주요 분석 로직

### 9.1 라인별 불량률 분석

`analyze_defect_rate_by_line()`은 생산 로그와 품질 검사 로그를 `date`, `line_id` 기준으로 병합한 뒤 `defect_qty / output_qty`로 불량률을 계산합니다. 이후 `line_id`별로 총 생산량, 총 검사량, 총 불량 수량, 평균 불량률, 최대 불량률을 집계하고 평균 불량률이 가장 높은 라인을 찾습니다.

주의할 점은 현재 `avg_defect_rate`가 날짜별 `defect_rate`의 단순 평균이라는 점입니다. 생산량 차이를 반영하려면 `total_defect_qty / total_output_qty` 기반의 weighted defect rate를 추가할 수 있습니다.

### 9.2 라인별 생산성 및 품질 요약

`summarize_performance_by_line()`은 `output_qty / operating_hours`로 생산성을 계산하고, 라인별 평균 생산성과 평균 불량률을 함께 요약합니다. 이 함수는 생산성 관점과 품질 관점을 동시에 제공합니다.

### 9.3 품질 이상 원인 후보 추론

`infer_quality_issue_candidates()`는 불량률과 센서 데이터를 함께 보고 우선 점검할 후보 라인을 정렬합니다. 평균 불량률, 최대 온도 초과 정도, 최대 진동 초과 정도를 반영해 규칙 기반 `risk_score`를 계산합니다.

```text
risk_score = avg_defect_rate * 100
           + max(max_temperature - 80, 0) * 0.3
           + max(max_vibration - 4, 0) * 2
```

이 점수는 머신러닝 모델이 예측한 원인 확률이 아닙니다. 실제 원인 확정이 아니라 현장에서 우선 점검할 후보를 좁히기 위한 휴리스틱 점수입니다.

### 9.4 센서 이상 탐지

`find_sensor_anomalies()`는 최근 N일 센서 로그에서 온도, 진동, 압력 중 하나라도 기준값 이상인 행을 이상 구간으로 추출합니다.

```text
TEMP_THRESHOLD = 85.0
VIBRATION_THRESHOLD = 4.5
PRESSURE_THRESHOLD = 2.8
```

이상 행에는 `temperature_high`, `vibration_high`, `pressure_high` 같은 reason이 붙습니다. summary의 총 이상 건수는 전체 이상 행 수를 사용하지만, evidence에는 대표로 앞 10개만 반환합니다.

## 10. Data Layer

### 10.1 CSV 기반 data_loader

`data_loader.py`는 생산 로그, 품질 검사 로그, 센서 로그 CSV를 pandas DataFrame으로 읽고 최근 N일 데이터만 필터링합니다. 최근 N일은 실제 오늘 날짜 기준이 아니라 CSV 데이터 안의 가장 최근 날짜 기준입니다.

```text
load_production_logs()
load_quality_logs()
load_sensor_logs()
filter_recent_by_date()
```

### 10.2 SQLite 준비 코드

프로젝트에는 SQLite 기반 DB 구조도 준비되어 있습니다.

```text
schema.sql
→ production_logs, quality_inspection, machine_sensor_logs 테이블 정의

init_db.py
→ schema.sql 실행 후 CSV 데이터를 SQLite에 적재

db_loader.py
→ SQLite에서 최근 N일 데이터 조회 helper 제공
```

다만 현재 Agent 핵심 분석 흐름은 DB가 아니라 CSV 기반 `data_loader.py`를 사용합니다. 따라서 DB는 확장 기반으로 준비된 상태입니다.

## 11. PromptTemplate과 답변 생성 방식

`build_answer()`는 LangChain `PromptTemplate`을 사용해 답변 생성용 `prompt_text`를 만들지만, 현재 버전에서는 실제 LLM 호출을 하지 않습니다. 최종 answer는 Tool 함수가 만든 `summary`를 그대로 사용합니다.

이 방식은 같은 입력과 같은 데이터에 대해 같은 결과가 나오는 deterministic한 응답 흐름을 먼저 검증하기 위한 선택입니다. 이후에는 동일한 evidence를 기반으로 LLM 답변 생성이나 LangSmith trace 확장으로 연결할 수 있습니다.

## 12. Trace Logging

현재 프로젝트에는 LangSmith가 직접 연동되어 있지 않습니다. 대신 `trace_logger.py`를 통해 `question`, `intent`, `tool_name`, `evidence_count`, `status` 등을 JSONL 파일로 남기는 자체 trace log가 있습니다.

로그는 `logs/agent_trace.jsonl`에 append 방식으로 누적됩니다. 서버가 종료되어도 파일이 유지되면 로그는 남아 있지만, Docker 컨테이너 내부에서 볼륨 없이 실행한 뒤 컨테이너를 삭제하면 로그가 사라질 수 있습니다.

## 13. AutoEncoder Model Endpoint

`/model/sensor-anomaly` endpoint는 자연어 입력이 아니라 센서값 3개를 직접 입력받습니다.

```text
temperature
vibration
pressure
```

`SensorAutoEncoder`는 3차원 입력을 encoder에서 2차원으로 압축하고, decoder에서 다시 3차원으로 복원합니다. 입력값과 복원값 사이의 평균 제곱 오차를 reconstruction error로 계산하고, 이를 `anomaly_score`로 사용합니다.

현재 모델은 학습된 weight를 로드한 운영 모델이 아닙니다. PyTorch 모델을 FastAPI endpoint로 서빙하는 구조를 보여주기 위한 기본 구현입니다. 실제 운영에서는 정상 센서 데이터 기반 학습, weight 저장/로드, 입력 정규화, 검증 데이터 기반 threshold 산정이 필요합니다.

## 14. Test

현재 테스트는 크게 세 범위로 나뉩니다.

```text
test_agent_flow.py
→ run_agent()를 호출해 자연어 입력이 intent/tool_name/answer/evidence로 이어지는지 검증

test_tools.py
→ Tool 함수를 직접 호출해 summary/evidence 형식과 샘플 데이터 기준 결과 검증

test_torch_model.py
→ predict_sensor_anomaly()가 anomaly_score와 is_anomaly를 반환하는지 검증
```

현재 테스트는 성공 흐름 중심입니다. 실무 수준으로 확장하려면 다음 테스트를 추가할 수 있습니다.

- FastAPI TestClient 기반 endpoint 테스트
- 입력 누락/타입 오류에 대한 422 validation 테스트
- 빈 입력, 지원하지 않는 입력, 키워드 겹침 테스트
- CSV 필수 컬럼 및 날짜 필터 테스트
- 데이터 품질 테스트
- Tool 실패 및 evidence 없는 경우 테스트
- DB loader 테스트
- trace log 생성 테스트
- Docker build 및 CI 재현성 테스트

## 15. Docker

Dockerfile은 프로젝트 실행 환경을 재현 가능하게 만들기 위한 파일입니다.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python scripts_generate_sample_data.py
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Docker 실행 예시:

```bash
docker build -t manufacturing-mcp-agent .
docker run -p 8000:8000 manufacturing-mcp-agent
```

## 16. GitHub Actions CI

GitHub Actions CI는 `main` 브랜치에 push되거나 pull request가 열릴 때 자동으로 실행됩니다. Ubuntu 환경에서 Python 3.11을 설정하고, requirements를 설치하고, 샘플 데이터를 생성한 뒤 pytest를 실행합니다.

```text
checkout repository
→ set up Python 3.11
→ install dependencies
→ generate sample data
→ run pytest
```

## 17. 실행 방법

### Local

```bash
pip install -r requirements.txt
python scripts_generate_sample_data.py
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

### Test

```bash
pytest
```

### Docker

```bash
docker build -t manufacturing-mcp-agent .
docker run -p 8000:8000 manufacturing-mcp-agent
```

## 18. 현재 구현 수준

구현된 것:

- FastAPI 기반 `/agent/query` endpoint
- LangGraph 기반 route_question → call_tool → build_answer workflow
- 규칙 기반 intent classification
- MCP-style Tool layer
- CSV 기반 제조 데이터 분석
- summary/evidence 기반 응답
- JSONL trace log
- PyTorch AutoEncoder model endpoint
- pytest 기반 핵심 흐름 검증
- Dockerfile
- GitHub Actions CI
- SQLite schema 및 loader 준비 코드

아직 구현되지 않았거나 제한적인 것:

- LLM 기반 intent classification
- LLM 답변 생성
- 사용자 입력에서 days, line_id 같은 tool_args 추출
- 실제 MCP protocol 기반 Tool server/client 분리
- Agent workflow에서 AutoEncoder Tool 호출
- DB 기반 분석 흐름 전환
- AutoEncoder 학습 weight 로드
- 검증 데이터 기반 threshold 산정
- FastAPI endpoint 통합 테스트
- 실패 케이스와 데이터 품질 테스트
- LangSmith 직접 연동

## 19. 한계와 개선 방향

현재 프로젝트는 샘플 CSV 기반이며, 실제 제조 현장의 복잡한 데이터 조건과는 차이가 있습니다. intent classification은 규칙 기반이므로 표현이 애매하거나 키워드가 겹치는 입력에는 한계가 있습니다. 또한 Tool 호출 인자가 `days=7`로 고정되어 있어 입력 문장에 포함된 기간이나 라인 조건을 반영하지 못합니다.

개선 방향은 다음과 같습니다.

- LLM 기반 JSON intent classification 추가
- question에서 `days`, `line_id`, `metric` 등 tool_args 추출
- CSV 기반 분석을 SQLite/PostgreSQL 기반 조회로 전환
- MCP protocol 기반 Tool server/client 구조 분리
- evidence 검증 node 추가
- LLM 답변 생성 node 추가
- AutoEncoder 학습, weight 저장/로드, threshold 산정
- FastAPI endpoint 테스트와 실패 케이스 테스트 강화
- LangSmith 또는 OpenTelemetry 기반 trace 확장
- Docker healthcheck, lint, type check, coverage CI 추가
