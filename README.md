# Manufacturing MCP Agent

MCP Tool 구조, LangGraph Workflow, FastAPI, SQLite, PyTorch 기반 제조 데이터 탐색·진단 AI Agent 백엔드 프로젝트입니다.

사용자가 제조 데이터에 대해 자연어로 질문하면, Agent가 질문 의도를 분류하고 필요한 Tool을 선택해 생산 로그, 품질 검사, 설비 센서 데이터를 분석한 뒤 `answer`와 `evidence`를 함께 반환합니다.

단순 챗봇처럼 답변만 생성하는 구조가 아니라, 다음 흐름을 중심으로 구성했습니다.

```text
질문 입력
→ intent 분류
→ MCP Tool 선택
→ 제조 데이터 분석
→ evidence 정리
→ grounded answer 생성
→ FastAPI JSON 응답
→ trace log 저장
```

---

## 1. Overview

이 프로젝트는 제조 현장의 생산 로그, 품질 검사, 설비 센서 데이터를 기반으로 사용자의 질문에 필요한 분석 Tool을 호출하는 AI Agent 백엔드 시스템입니다.

주요 목표는 다음과 같습니다.

- 제조 데이터 질문을 intent로 분류
- intent에 따라 적절한 MCP Tool 선택
- SQLite 기반 제조 샘플 데이터 조회
- 생산성, 불량률, 설비 이상, 품질 원인 후보 분석
- PyTorch SensorAutoEncoder 기반 센서 이상탐지 endpoint 제공
- FastAPI Swagger에서 API 응답 확인
- pytest, Docker, GitHub Actions 기반 실행·검증 흐름 구성

---

## 2. Why I Built This

제조 현장 데이터는 생산 로그, 품질 검사, 설비 센서처럼 여러 형태로 나뉘어 있습니다.

일반적인 챗봇 방식은 사용자의 질문에 바로 답변을 생성할 수 있지만, 실제 데이터 기반 시스템에서는 다음 질문을 함께 해결해야 합니다.

- 어떤 데이터를 조회해야 하는가?
- 어떤 분석 Tool을 호출해야 하는가?
- 어떤 근거를 사용해 답변했는가?
- 답변이 실제 데이터에 기반하고 있는가?
- 모델 추론 결과를 API로 어떻게 제공할 것인가?

이 프로젝트는 이러한 문제를 해결하기 위해 질문을 바로 답변하지 않고, `intent routing → Tool calling → evidence formatting → answer generation` 구조로 설계했습니다.

---

## 3. Key Features

- 제조 샘플 데이터 생성
- SQLite DB schema 및 CSV-to-DB pipeline 구성
- 생산 로그, 품질 검사, 설비 센서 데이터 관리
- 질문 intent 분류
- MCP Tool 구조 기반 분석 기능 분리
- LangGraph 기반 Agent workflow 구성
- LangChain PromptTemplate 기반 grounded answer 정책 분리
- FastAPI `/agent/query` endpoint 제공
- PyTorch SensorAutoEncoder 기반 `/model/sensor-anomaly` endpoint 제공
- Agent trace logging JSONL 저장
- pytest 기반 기능 테스트
- Docker / Docker Compose 실행 환경 구성
- GitHub Actions CI 기초 구성

---

## 4. Project Structure

```text
manufacturing-mcp-agent/
├─ app/
│  ├─ agent/              # LangGraph Agent workflow
│  ├─ db/                 # SQLite DB 연결 및 데이터 조회
│  ├─ mcp_server/         # MCP Tool / Tool server 구조
│  ├─ models/             # PyTorch SensorAutoEncoder 모델
│  ├─ services/           # 서비스 로직
│  ├─ config.py           # 설정값
│  ├─ main.py             # FastAPI 실행 진입점
│  └─ __init__.py
├─ data/                  # 제조 샘플 데이터 및 DB
├─ docs/                  # 설계 문서
├─ langflow/              # LangFlow 설계 자료
├─ logs/                  # Agent trace log
├─ tests/                 # pytest 테스트 코드
├─ .github/               # GitHub Actions workflow
├─ Dockerfile
├─ docker-compose.yml
├─ pytest.ini
├─ requirements.txt
├─ scripts_generate_sample_data.py
└─ README.md
```

---

## 5. Architecture

### Agent Query Flow

```text
사용자 질문 입력
→ FastAPI /agent/query
→ LangGraph route_question
→ intent 분류
→ MCP Tool 선택
→ 제조 데이터 분석
→ answer / evidence 반환
→ trace log 저장
```

### Model Serving Flow

```text
센서 입력값 수신
→ FastAPI /model/sensor-anomaly
→ PyTorch SensorAutoEncoder
→ anomaly_score 계산
→ threshold 비교
→ is_anomaly 반환
```

### Layer Structure

```text
API Layer
→ Agent Workflow Layer
→ MCP Tool Layer
→ Data Pipeline Layer
→ Model Serving Layer
→ Logging / Test Layer
```

각 계층을 분리해 질문 분류, Tool 호출, 데이터 분석, 답변 생성, 모델 추론을 독립적으로 확인하고 개선할 수 있도록 구성했습니다.

---

## 6. Tech Stack

- Python
- FastAPI
- SQLite
- SQL
- pandas
- PyTorch
- LangGraph
- LangChain PromptTemplate
- Docker
- Docker Compose
- pytest
- GitHub Actions

---

## 7. MCP Tool Design

Agent가 모든 분석 로직을 직접 처리하지 않도록, 제조 데이터 분석 기능을 Tool 단위로 분리했습니다.

| Tool | Role |
|---|---|
| `defect_rate_by_line` | 라인별 불량률 계산 |
| `machine_anomalies` | 설비 센서 이상 탐지 |
| `summarize_line_performance` | 라인별 생산성 및 품질 요약 |
| `quality_issue_candidates` | 품질 이상 원인 후보 추정 |

질문 intent에 따라 필요한 Tool을 선택하고, Tool 결과는 `answer`와 `evidence` 형식으로 정리됩니다.

---

## 8. Agent Workflow

LangGraph 기반 workflow는 다음 단계를 중심으로 구성했습니다.

```text
route_question
→ call_tool
→ build_answer
```

- `route_question`: 사용자 질문을 intent로 분류
- `call_tool`: intent에 맞는 MCP Tool 호출
- `build_answer`: Tool 결과를 기반으로 grounded answer 생성

이 구조를 통해 Agent가 어떤 단계를 거쳐 결과를 생성했는지 추적할 수 있습니다.

---

## 9. API Endpoints

### `/agent/query`

제조 데이터 관련 자연어 질문을 입력받아 intent, tool_name, answer, evidence를 반환합니다.

```text
POST /agent/query
```

### `/model/sensor-anomaly`

센서 입력값을 받아 PyTorch SensorAutoEncoder 기반 anomaly_score를 반환합니다.

```text
POST /model/sensor-anomaly
```

---

## 10. How to Run

### 1) Create and activate virtual environment

Windows PowerShell 기준:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Run tests

```powershell
pytest -v
```

실행 확인 결과:

```text
collected 9 items
9 passed in 11.13s
```

### 4) Run FastAPI server

```powershell
uvicorn app.main:app --reload
```

실행 후 Swagger UI에서 API를 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

---

## 11. Verified Execution

로컬 Windows PowerShell 환경에서 다음 항목을 확인했습니다.

```text
1. GitHub 원격 저장소와 로컬 코드 동기화 확인
2. 프로젝트 파일 구조 확인
3. pytest -v 실행
4. 9개 테스트 전체 통과
5. FastAPI 서버 실행
6. Swagger UI에서 /agent/query 응답 확인
7. Swagger UI에서 /model/sensor-anomaly 응답 확인
```

### Test Result

```text
platform win32 -- Python 3.11.9
collected 9 items

tests/test_agent_flow.py::test_agent_routes_defect_question PASSED
tests/test_agent_flow.py::test_agent_routes_anomaly_question PASSED
tests/test_agent_flow.py::test_agent_routes_performance_question PASSED
tests/test_agent_flow.py::test_agent_routes_quality_candidate_question PASSED
tests/test_tools.py::test_defect_rate_tool_returns_evidence PASSED
tests/test_tools.py::test_anomaly_tool_returns_summary PASSED
tests/test_tools.py::test_performance_tool_returns_evidence PASSED
tests/test_tools.py::test_quality_issue_candidates_returns_line_c PASSED
tests/test_torch_model.py::test_predict_sensor_anomaly_returns_score PASSED

9 passed in 11.13s
```

---

## 12. API Example - Agent Query

### Request

```json
{
  "question": "라인별 불량률을 알려줘"
}
```

### Response

```json
{
  "question": "라인별 불량률을 알려줘",
  "intent": "line_performance",
  "tool_name": "summarize_line_performance",
  "answer": "최근 7일 기준 생산성이 가장 높은 라인은 LINE_D이며, 평균 시간당 생산량은 146.1개입니다. 품질 측면에서는 LINE_C의 평균 불량률이 4.39%로 가장 높습니다.",
  "evidence": [
    {
      "line_id": "LINE_D",
      "output_qty": 7874,
      "operating_hours": 54.07,
      "defect_qty": 128,
      "avg_defect_rate": 0.016108740174909774,
      "avg_productivity": 146.08852263069417
    },
    {
      "line_id": "LINE_C",
      "output_qty": 7677,
      "operating_hours": 56.3,
      "defect_qty": 340,
      "avg_defect_rate": 0.04394263227427786,
      "avg_productivity": 136.6009404825025
    },
    {
      "line_id": "LINE_B",
      "output_qty": 7291,
      "operating_hours": 57.35,
      "defect_qty": 223,
      "avg_defect_rate": 0.030711468800569932,
      "avg_productivity": 127.21543371901414
    },
    {
      "line_id": "LINE_A",
      "output_qty": 5939,
      "operating_hours": 55.55,
      "defect_qty": 123,
      "avg_defect_rate": 0.02058405764997165,
      "avg_productivity": 107.22742343544272
    }
  ]
}
```

이 질문은 라인별 불량률을 묻지만, 라인별 생산성과 품질 지표를 함께 요약하는 `line_performance` intent로 라우팅됩니다.  
응답에는 평균 불량률과 평균 생산성이 함께 포함되어 라인별 운영 상태를 함께 확인할 수 있습니다.

---

## 13. API Example - Sensor Anomaly Model

### Request

```json
{
  "temperature": 25,
  "vibration": 0.3,
  "pressure": 101,
  "humidity": 45
}
```

### Response

```json
{
  "temperature": 25,
  "vibration": 0.3,
  "pressure": 101,
  "anomaly_score": 2680.360595703125,
  "threshold": 1000,
  "is_anomaly": true,
  "model": "SensorAutoEncoder",
  "note": "현재 모델은 포트폴리오용 기본 AutoEncoder 구조입니다. 실제 운영에서는 정상 센서 데이터로 학습한 weight와 검증 기반 threshold가 필요합니다."
}
```

현재 endpoint는 temperature, vibration, pressure, humidity를 입력으로 받으며, 응답은 주요 센서값과 anomaly_score, threshold, is_anomaly를 중심으로 반환합니다.

---

## 14. My Role

- 제조 샘플 데이터 구조 설계
- 생산 로그, 품질 검사, 설비 센서 샘플 데이터 생성
- SQLite DB schema 구성
- CSV-to-DB pipeline 구성
- 질문 intent 분류 규칙 구현
- MCP Tool 구조 설계
- 제조 데이터 분석 Tool 함수 분리
- LangGraph 기반 Agent workflow 구현
- LangChain PromptTemplate 기반 grounded answer 정책 분리
- FastAPI `/agent/query` endpoint 구현
- PyTorch SensorAutoEncoder 기반 `/model/sensor-anomaly` endpoint 구현
- Agent trace logging JSONL 저장
- pytest 기반 기능 테스트 구성
- Docker / Docker Compose 실행 환경 구성
- GitHub Actions CI 기초 구성
- README 및 실행 문서 작성

---

## 15. Problem & Solution

### Problem

제조 데이터는 생산 로그, 품질 검사, 설비 센서처럼 여러 형태로 나뉘어 있습니다.

단순 챗봇 방식으로는 다음을 명확히 관리하기 어렵습니다.

- 어떤 데이터를 조회해야 하는지
- 어떤 Tool을 호출해야 하는지
- 어떤 근거를 사용해 답변했는지
- 모델 추론 결과를 API 형태로 어떻게 제공할지

### Solution

사용자 질문을 intent로 분류하고, intent에 따라 MCP Tool을 선택하도록 구성했습니다.

각 Tool은 생산 로그, 품질 검사, 설비 센서 데이터를 분석하고, 결과를 `answer`와 `evidence`로 반환합니다.

또한 PyTorch 기반 센서 이상탐지 endpoint를 별도로 제공해, Agent API와 모델 서빙 API를 함께 구성했습니다.

---

## 16. Improvement Process

개발 과정에서 다음 문제를 개선했습니다.

### 1) Tool Routing 개선

초기에는 질문에 "이상"과 "품질"이 함께 포함될 때 잘못된 Tool로 라우팅되는 문제가 있었습니다.

이를 해결하기 위해 단순 키워드 포함 여부만 보지 않고, 원인·후보·왜와 같은 목적 단어를 우선 판별하도록 intent routing 우선순위를 조정했습니다.

### 2) Docker 실행 안정성 개선

Windows 가상환경 전체를 freeze한 requirements 때문에 Docker Linux 환경에서 `pywin32` 오류가 발생했습니다.

이후 실제 실행에 필요한 패키지만 남기는 방식으로 `requirements.txt`를 최소화해 Docker 실행 안정성을 개선했습니다.

---

## 17. What I Learned

이 프로젝트를 통해 AI Agent 개발은 모델 호출만으로 완성되지 않는다는 점을 배웠습니다.

실제로 활용 가능한 Agent를 만들기 위해서는 다음 요소가 함께 설계되어야 합니다.

- 데이터 구조
- Tool 설계
- Workflow
- API 응답 구조
- 근거 기반 답변 정책
- 모델 추론 endpoint
- 테스트와 실행 환경

또한 Agent가 모든 로직을 직접 처리하는 것보다, 질문 분류와 Tool 호출, 데이터 분석, 답변 생성을 분리하는 방식이 테스트와 개선에 유리하다는 점을 확인했습니다.

---

## 18. Limitations & Improvements

현재 프로젝트는 포트폴리오용 샘플 제조 데이터와 기본 AutoEncoder 구조를 기반으로 구성되어 있습니다.

실제 서비스에 적용하기 위해서는 다음 보완이 필요합니다.

- 실제 제조 현장 데이터 연동
- 운영 DB 전환
- 실제 정상 센서 데이터로 학습한 model weight 적용
- validation 기반 threshold 설정
- 모델 성능 검증
- API 요청 로그 및 모니터링
- 권한 관리 및 보안
- 실시간 데이터 스트리밍
- Redis 또는 Kafka 기반 비동기 처리
- LangSmith 등 trace 관리 도구 연동
- 실제 MCP Client 연동
- 클라우드 배포 환경 구성

---

## 19. Interview Summary

Manufacturing MCP Agent는 제조 데이터를 기반으로 사용자의 질문을 처리하고, Agent가 필요한 Tool을 선택해 DB 조회나 모델 추론 결과를 연결하는 AI Agent 백엔드 프로젝트입니다.

FastAPI로 API endpoint를 구성하고, 제조 데이터는 SQLite에 저장했으며, LangGraph workflow를 통해 질문 intent에 따라 적절한 Tool을 호출하도록 설계했습니다.

또한 PyTorch SensorAutoEncoder 기반 `/model/sensor-anomaly` endpoint를 제공해 모델 결과를 API 형태로 확인할 수 있도록 구성했습니다.

로컬 환경에서 pytest 9개 테스트 통과, Swagger 기반 `/agent/query`, `/model/sensor-anomaly` 응답을 확인했습니다.

이 프로젝트의 핵심은 질문을 바로 답변하지 않고, 질문 의도 분류 → Tool 선택 → 데이터 분석 → 근거 반환 → API 응답으로 이어지는 구조를 구현한 점입니다.
