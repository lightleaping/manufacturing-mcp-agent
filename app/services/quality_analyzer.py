from __future__ import annotations

from app.services.data_loader import (
    load_production_logs,
    load_quality_logs,
    load_sensor_logs,
    filter_recent_by_date,
)


def analyze_defect_rate_by_line(days: int = 7) -> dict:
    """
    최근 N일 기준 라인별 불량률을 계산하고,
    평균 불량률이 가장 높은 라인을 찾습니다.
    """
    production = filter_recent_by_date(
        load_production_logs(),
        "date",
        days,
    )
    quality = filter_recent_by_date(
        load_quality_logs(),
        "date",
        days,
    )

    merged = production.merge(
        quality,
        on=["date", "line_id"],
        how="left",
    )

    merged["defect_rate"] = merged["defect_qty"] / merged["output_qty"]

    grouped = (
        merged.groupby("line_id", as_index=False)
        .agg(
            output_qty=("output_qty", "sum"),
            inspected_qty=("inspected_qty", "sum"),
            defect_qty=("defect_qty", "sum"),
            avg_defect_rate=("defect_rate", "mean"),
            max_defect_rate=("defect_rate", "max"),
        )
        .sort_values("avg_defect_rate", ascending=False)
    )

    top = grouped.iloc[0].to_dict()
    evidence = grouped.head(3).to_dict(orient="records")

    summary = (
        f"최근 {days}일 기준 불량률이 가장 높은 라인은 {top['line_id']}입니다. "
        f"평균 불량률은 {top['avg_defect_rate']:.2%}, "
        f"총 생산량은 {int(top['output_qty'])}개, "
        f"총 불량 수량은 {int(top['defect_qty'])}개입니다."
    )

    return {
        "summary": summary,
        "evidence": evidence,
    }


def summarize_performance_by_line(days: int = 7) -> dict:
    """
    최근 N일 기준 라인별 생산성과 품질 상태를 요약합니다.
    """
    production = filter_recent_by_date(
        load_production_logs(),
        "date",
        days,
    )
    quality = filter_recent_by_date(
        load_quality_logs(),
        "date",
        days,
    )

    merged = production.merge(
        quality,
        on=["date", "line_id"],
        how="left",
    )

    merged["defect_rate"] = merged["defect_qty"] / merged["output_qty"]
    merged["productivity"] = merged["output_qty"] / merged["operating_hours"]

    grouped = (
        merged.groupby("line_id", as_index=False)
        .agg(
            output_qty=("output_qty", "sum"),
            operating_hours=("operating_hours", "sum"),
            defect_qty=("defect_qty", "sum"),
            avg_defect_rate=("defect_rate", "mean"),
            avg_productivity=("productivity", "mean"),
        )
        .sort_values("avg_productivity", ascending=False)
    )

    best_productivity = grouped.iloc[0].to_dict()
    worst_quality = grouped.sort_values(
        "avg_defect_rate",
        ascending=False,
    ).iloc[0].to_dict()

    summary = (
        f"최근 {days}일 기준 생산성이 가장 높은 라인은 "
        f"{best_productivity['line_id']}이며, "
        f"평균 시간당 생산량은 {best_productivity['avg_productivity']:.1f}개입니다. "
        f"품질 측면에서는 {worst_quality['line_id']}의 평균 불량률이 "
        f"{worst_quality['avg_defect_rate']:.2%}로 가장 높습니다."
    )

    return {
        "summary": summary,
        "evidence": grouped.to_dict(orient="records"),
    }


def infer_quality_issue_candidates(days: int = 7) -> dict:
    """
    불량률과 센서 데이터를 함께 보고 품질 이상 원인 후보를 추정합니다.
    실제 원인을 확정하는 것이 아니라, 우선 점검할 후보를 제안합니다.
    """
    production = filter_recent_by_date(
        load_production_logs(),
        "date",
        days,
    )
    quality = filter_recent_by_date(
        load_quality_logs(),
        "date",
        days,
    )
    sensor = filter_recent_by_date(
        load_sensor_logs(),
        "timestamp",
        days,
    )

    merged = production.merge(
        quality,
        on=["date", "line_id"],
        how="left",
    )
    merged["defect_rate"] = merged["defect_qty"] / merged["output_qty"]

    defect_by_line = (
        merged.groupby("line_id", as_index=False)
        .agg(
            avg_defect_rate=("defect_rate", "mean"),
            defect_qty=("defect_qty", "sum"),
        )
    )

    sensor_by_line = (
        sensor.groupby("line_id", as_index=False)
        .agg(
            avg_temperature=("temperature", "mean"),
            max_temperature=("temperature", "max"),
            avg_vibration=("vibration", "mean"),
            max_vibration=("vibration", "max"),
            avg_pressure=("pressure", "mean"),
            max_pressure=("pressure", "max"),
        )
    )

    result = defect_by_line.merge(
        sensor_by_line,
        on="line_id",
        how="left",
    )

    result["risk_score"] = (
        result["avg_defect_rate"] * 100
        + (result["max_temperature"] - 80).clip(lower=0) * 0.3
        + (result["max_vibration"] - 4).clip(lower=0) * 2
    )

    result = result.sort_values("risk_score", ascending=False)

    top = result.iloc[0].to_dict()
    evidence = result.head(3).to_dict(orient="records")

    summary = (
        f"최근 {days}일 기준 품질 이상 원인 후보가 가장 높은 라인은 "
        f"{top['line_id']}입니다. "
        f"평균 불량률 {top['avg_defect_rate']:.2%}, "
        f"최대 온도 {top['max_temperature']:.1f}, "
        f"최대 진동 {top['max_vibration']:.2f}가 함께 관찰되었습니다. "
        f"따라서 해당 라인의 설비 조건을 우선 점검할 필요가 있습니다. "
        f"단, 이 결과는 샘플 데이터 기반의 규칙 분석이므로 실제 원인 확정에는 추가 현장 데이터가 필요합니다."
    )

    return {
        "summary": summary,
        "evidence": evidence,
    }