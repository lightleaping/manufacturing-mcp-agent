from __future__ import annotations

from app.services.data_loader import load_sensor_logs, filter_recent_by_date


TEMP_THRESHOLD = 85.0
VIBRATION_THRESHOLD = 4.5
PRESSURE_THRESHOLD = 2.8


def find_sensor_anomalies(days: int = 7) -> dict:
    """
    최근 N일 기준 설비 센서 데이터에서 임계값을 초과한 이상 구간을 찾습니다.
    """
    sensor = filter_recent_by_date(
        load_sensor_logs(),
        "timestamp",
        days,
    )

    anomalies = sensor[
        (sensor["temperature"] >= TEMP_THRESHOLD)
        | (sensor["vibration"] >= VIBRATION_THRESHOLD)
        | (sensor["pressure"] >= PRESSURE_THRESHOLD)
    ].copy()

    if anomalies.empty:
        return {
            "summary": f"최근 {days}일 기준 임계값을 초과한 설비 센서 이상 구간은 발견되지 않았습니다.",
            "evidence": [],
        }

    anomalies["reason"] = anomalies.apply(_build_reason, axis=1)

    evidence = (
        anomalies.sort_values("timestamp")
        .head(10)
        .to_dict(orient="records")
    )

    line_counts = anomalies.groupby("line_id").size().sort_values(ascending=False)
    top_line = line_counts.index[0]
    top_count = int(line_counts.iloc[0])

    summary = (
        f"최근 {days}일 기준 센서 이상은 총 {len(anomalies)}건 발견되었습니다. "
        f"가장 많이 발생한 라인은 {top_line}이며 {top_count}건입니다. "
        f"온도 기준은 {TEMP_THRESHOLD}, 진동 기준은 {VIBRATION_THRESHOLD}, "
        f"압력 기준은 {PRESSURE_THRESHOLD}입니다."
    )

    return {
        "summary": summary,
        "evidence": evidence,
    }


def _build_reason(row) -> str:
    reasons = []

    if row["temperature"] >= TEMP_THRESHOLD:
        reasons.append("temperature_high")

    if row["vibration"] >= VIBRATION_THRESHOLD:
        reasons.append("vibration_high")

    if row["pressure"] >= PRESSURE_THRESHOLD:
        reasons.append("pressure_high")

    return ",".join(reasons)