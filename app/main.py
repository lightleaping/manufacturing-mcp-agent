from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.agent.graph import run_agent

from app.services.torch_anomaly_service import predict_sensor_anomaly

app = FastAPI(
    title="Manufacturing MCP Agent",
    description="MCP Tool과 LangGraph를 활용한 제조 데이터 탐색·진단 Agent API",
    version="0.1.0",
)


class AgentQueryRequest(BaseModel):
    question: str = Field(
        ...,
        examples=["최근 7일간 불량률이 가장 높은 라인을 찾아줘."],
    )


class AgentQueryResponse(BaseModel):
    question: str
    intent: str
    tool_name: str
    answer: str
    evidence: list[dict]

class SensorAnomalyRequest(BaseModel):
    temperature: float = Field(..., examples=[95.7])
    vibration: float = Field(..., examples=[5.6])
    pressure: float = Field(..., examples=[2.4])


class SensorAnomalyResponse(BaseModel):
    temperature: float
    vibration: float
    pressure: float
    anomaly_score: float
    threshold: float
    is_anomaly: bool
    model: str
    note: str

@app.get("/")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "manufacturing-mcp-agent",
        "message": "Use POST /agent/query or open /docs.",
    }


@app.post("/agent/query", response_model=AgentQueryResponse)
def query_agent(request: AgentQueryRequest) -> AgentQueryResponse:
    result = run_agent(request.question)
    return AgentQueryResponse(**result)

@app.post("/model/sensor-anomaly", response_model=SensorAnomalyResponse)
def serve_sensor_anomaly_model(
    request: SensorAnomalyRequest,
) -> SensorAnomalyResponse:
    result = predict_sensor_anomaly(
        temperature=request.temperature,
        vibration=request.vibration,
        pressure=request.pressure,
    )
    return SensorAnomalyResponse(**result)