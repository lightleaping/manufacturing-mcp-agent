# __future__ 모듈에서 annotations 기능을 가져옵니다.
# annotations는 타입 힌트를 즉시 평가하지 않고 나중에 처리하도록 도와줍니다.
# 예를 들어 함수 반환 타입이나 클래스 타입 힌트를 더 유연하게 사용할 수 있게 합니다.
from __future__ import annotations

# FastAPI는 API 서버 애플리케이션을 만들기 위한 클래스입니다.
# 여기서는 app = FastAPI(...) 형태로 서버 객체를 만들 때 사용합니다.
from fastapi import FastAPI

# BaseModel은 Pydantic의 데이터 검증 모델을 만들 때 사용합니다.
# 요청 body와 응답 body의 구조를 class로 정의할 수 있습니다.
#
# Field는 각 필드에 추가 정보를 붙일 때 사용합니다.
# 예를 들어 필수값 여부, Swagger 예시값 등을 설정할 수 있습니다.
from pydantic import BaseModel, Field

# Agent workflow를 실행하는 함수입니다.
# /agent/query API가 호출되면 최종적으로 이 run_agent(question)가 실행됩니다.
# 즉, 사용자 질문을 Agent workflow로 넘기는 핵심 연결 지점입니다.
from app.agent.graph import run_agent

# 센서 이상 탐지 모델 endpoint에서 사용할 서비스 함수입니다.
# /model/sensor-anomaly API가 호출되면 이 함수가 실제 anomaly score를 계산합니다.
from app.services.torch_anomaly_service import predict_sensor_anomaly


# FastAPI 애플리케이션 객체를 생성합니다.
# 이 app 객체에 endpoint를 등록하면 FastAPI 서버에서 API로 사용할 수 있습니다.
app = FastAPI(
    # Swagger UI 상단에 표시될 API 이름입니다.
    title="Manufacturing MCP Agent",

    # Swagger UI에 표시될 API 설명입니다.
    # 이 프로젝트가 MCP Tool과 LangGraph를 활용한 제조 데이터 탐색·진단 Agent API라는 것을 설명합니다.
    description="MCP Tool과 LangGraph를 활용한 제조 데이터 탐색·진단 Agent API",

    # API 버전입니다.
    # 현재 프로젝트 버전이 0.1.0임을 나타냅니다.
    version="0.1.0",
)


# /agent/query API가 받을 요청 body 구조입니다.
# 사용자가 Agent에게 질문을 보낼 때 이 모델을 사용합니다.
class AgentQueryRequest(BaseModel):
    # question은 사용자가 입력하는 자연어 질문입니다.
    # str 타입이므로 문자열이어야 합니다.
    question: str = Field(
        # ... 은 이 값이 필수 입력값이라는 뜻입니다.
        # 즉, question 없이 /agent/query를 호출하면 검증 오류가 발생합니다.
        ...,

        # Swagger UI에서 보여줄 예시 질문입니다.
        # 실제 실행 로직에 직접 영향을 주는 값은 아니고, 문서화/테스트 편의용입니다.
        examples=["최근 7일간 불량률이 가장 높은 라인을 찾아줘."],
    )


# /agent/query API가 반환할 응답 body 구조입니다.
# run_agent()가 반환한 dict가 이 구조에 맞는지 검증됩니다.
class AgentQueryResponse(BaseModel):
    # 사용자가 보낸 질문을 그대로 응답에 포함합니다.
    question: str

    # Agent가 classify_intent()로 분류한 질문 의도입니다.
    # 예: defect_rate, machine_anomaly, line_performance, quality_issue_candidates
    intent: str

    # intent에 따라 선택된 Tool 이름입니다.
    # 예: get_defect_rate_by_line, detect_machine_anomalies 등
    tool_name: str

    # 최종 사용자에게 보여줄 답변입니다.
    # 현재 graph.py 기준으로는 외부 LLM 답변이 아니라 Tool의 summary가 들어갑니다.
    answer: str

    # 답변의 근거 데이터입니다.
    # 각 Tool이 반환한 evidence 리스트가 여기에 들어갑니다.
    evidence: list[dict]


# /model/sensor-anomaly API가 받을 요청 body 구조입니다.
# 이 endpoint는 Agent 질문 처리가 아니라 센서 이상 탐지 모델 서빙용입니다.
class SensorAnomalyRequest(BaseModel):
    # 온도 입력값입니다.
    # float 타입이므로 소수점 숫자를 받을 수 있습니다.
    # Field(..., examples=[95.7])이므로 필수값이고 Swagger 예시는 95.7입니다.
    temperature: float = Field(..., examples=[95.7])

    # 진동 입력값입니다.
    vibration: float = Field(..., examples=[5.6])

    # 압력 입력값입니다.
    pressure: float = Field(..., examples=[2.4])


# /model/sensor-anomaly API가 반환할 응답 body 구조입니다.
class SensorAnomalyResponse(BaseModel):
    # 요청으로 들어온 온도 값입니다.
    temperature: float

    # 요청으로 들어온 진동 값입니다.
    vibration: float

    # 요청으로 들어온 압력 값입니다.
    pressure: float

    # 모델이 계산한 이상 점수입니다.
    anomaly_score: float

    # 이상 여부를 판단하는 기준값입니다.
    threshold: float

    # anomaly_score가 threshold를 넘었는지에 따라 결정되는 이상 여부입니다.
    is_anomaly: bool

    # 사용한 모델 이름입니다.
    model: str

    # 모델 응답에 대한 설명 문장입니다.
    note: str


# GET / endpoint를 등록합니다.
# 브라우저에서 http://127.0.0.1:8000/ 로 접속했을 때 실행됩니다.
@app.get("/")
def health_check() -> dict:
    # 서버가 정상적으로 실행 중인지 확인하기 위한 간단한 응답입니다.
    return {
        # 서버 상태입니다.
        "status": "ok",

        # 서비스 이름입니다.
        "service": "manufacturing-mcp-agent",

        # 사용자가 어떤 endpoint를 사용하면 되는지 안내합니다.
        "message": "Use POST /agent/query or open /docs.",
    }


# POST /agent/query endpoint를 등록합니다.
# 이 API는 제조 데이터 질문을 Agent workflow로 보내는 입구입니다.
#
# response_model=AgentQueryResponse는
# 이 endpoint의 최종 응답이 AgentQueryResponse 구조를 따라야 한다는 뜻입니다.
@app.post("/agent/query", response_model=AgentQueryResponse)
def query_agent(request: AgentQueryRequest) -> AgentQueryResponse:
    # request는 FastAPI가 요청 body를 AgentQueryRequest 모델로 검증한 객체입니다.
    # 사용자가 JSON으로 {"question": "..."}을 보내면,
    # 그 값이 request.question에 들어갑니다.
    #
    # run_agent(request.question)는 실제 Agent workflow를 실행합니다.
    # 여기서 app/agent/graph.py의 run_agent 함수로 넘어갑니다.
    result = run_agent(request.question)

    # run_agent()가 반환한 dict를 AgentQueryResponse 모델로 변환합니다.
    #
    # **result는 dictionary unpacking입니다.
    # 예를 들어 result가 아래와 같다면:
    # {
    #   "question": "...",
    #   "intent": "...",
    #   "tool_name": "...",
    #   "answer": "...",
    #   "evidence": [...]
    # }
    #
    # AgentQueryResponse(
    #   question=result["question"],
    #   intent=result["intent"],
    #   tool_name=result["tool_name"],
    #   answer=result["answer"],
    #   evidence=result["evidence"],
    # )
    # 와 같은 의미입니다.
    return AgentQueryResponse(**result)


# POST /model/sensor-anomaly endpoint를 등록합니다.
# 이 API는 Agent 질문 처리와 별개로, 센서 입력값을 모델에 넣어 이상 여부를 판단하는 endpoint입니다.
@app.post("/model/sensor-anomaly", response_model=SensorAnomalyResponse)
def serve_sensor_anomaly_model(
    # FastAPI가 요청 body를 SensorAnomalyRequest 모델로 검증한 객체입니다.
    request: SensorAnomalyRequest,
) -> SensorAnomalyResponse:
    # 요청으로 들어온 temperature, vibration, pressure 값을
    # predict_sensor_anomaly 함수에 넘깁니다.
    #
    # 실제 anomaly_score 계산과 threshold 비교는
    # app/services/torch_anomaly_service.py 쪽에서 수행합니다.
    result = predict_sensor_anomaly(
        temperature=request.temperature,
        vibration=request.vibration,
        pressure=request.pressure,
    )

    # predict_sensor_anomaly()가 반환한 dict를
    # SensorAnomalyResponse 구조로 변환해 응답합니다.
    return SensorAnomalyResponse(**result)