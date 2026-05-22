from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path("logs")
TRACE_LOG_PATH = LOG_DIR / "agent_trace.jsonl"


def write_agent_trace(
    question: str,
    intent: str,
    tool_name: str,
    evidence_count: int,
    status: str = "success",
    extra: dict[str, Any] | None = None,
) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    record = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "question": question,
        "intent": intent,
        "tool_name": tool_name,
        "evidence_count": evidence_count,
        "status": status,
    }

    if extra:
        record["extra"] = extra

    with TRACE_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")