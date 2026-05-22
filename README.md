\# Manufacturing MCP Agent



제조 데이터 탐색·진단을 위한 MCP 기반 AI Agent 시스템입니다.



\## 프로젝트 목적



사용자가 제조 현장 데이터에 대해 자연어로 질문하면, Agent가 질문 유형을 판단하고 필요한 MCP Tool을 호출해 생산 로그, 품질 검사, 설비 센서 데이터를 분석한 뒤 근거 기반 답변을 반환하는 시스템을 구현합니다.



이 프로젝트는 AI Agent Engineer 직무에서 요구하는 MCP Server, Agent Workflow, 제조 데이터 연동, Data Pipeline, FastAPI, Docker 기반 실행 환경을 포트폴리오 프로젝트로 보완하기 위해 진행합니다.



\## 주요 기능



1\. 라인별 불량률 분석

2\. 설비 센서 이상 탐지

3\. 라인별 생산성 및 품질 요약

4\. 품질 이상 원인 후보 추정



\## 예시 질문



\- 최근 7일간 불량률이 가장 높은 라인을 찾아줘.

\- 설비 온도나 진동이 비정상적으로 높은 구간이 있어?

\- 라인별 생산성과 품질 상태를 요약해줘.

\- 품질 이상 원인 후보를 데이터 근거와 함께 알려줘.



\## 기술 스택 예정



\- Python

\- FastAPI

\- MCP

\- LangGraph

\- pandas

\- SQLite 또는 CSV

\- Docker

\- GitHub Actions

\- pytest



\## 프로젝트 구조 예정



```text

User Question

→ FastAPI

→ LangGraph Agent

→ Question Router

→ MCP Tool

→ Manufacturing Data Analysis

→ Evidence

→ Grounded Answer

