"""Response-priority scoring for synthetic water utility review."""

from __future__ import annotations

import pandas as pd


def build_response_priorities(scores: pd.DataFrame, zones: pd.DataFrame) -> pd.DataFrame:
    """Convert anomaly scores into human-review response priorities."""
    zone_lookup = zones.set_index("zone_id")
    rows = []
    for row in scores.itertuples(index=False):
        zone = zone_lookup.loc[row.zone_id]
        health_weight = 0.18 if zone.zone_type in ["hospital", "school"] else 0.08
        priority_score = min(
            1.0,
            0.54 * float(row.overall_response_risk_score)
            + 0.18 * float(row.critical_customer_index)
            + 0.12 * (1 - float(row.service_equity_index))
            + 0.08 * float(row.pipe_age_index)
            + health_weight,
        )
        rows.append({
            "sensor_id": row.sensor_id,
            "zone_id": row.zone_id,
            "zone_type": zone.zone_type,
            "top_risk_type": row.top_risk_type,
            "response_priority_score": round(float(priority_score), 4),
            "priority_band": _band(priority_score),
            "recommended_review_action": _action(row.top_risk_type, priority_score),
            "review_window": _window(priority_score),
            "decision_boundary": "engineering and water-quality review prompt only; not emergency public-health instruction",
        })
    return pd.DataFrame(rows).sort_values("response_priority_score", ascending=False).reset_index(drop=True)


def priority_summary(priority: pd.DataFrame) -> dict[str, int | float]:
    if priority.empty:
        return {"urgent_review_count": 0, "mean_response_priority_score": 0.0}
    return {
        "urgent_review_count": int(priority["priority_band"].isin(["urgent", "critical"]).sum()),
        "critical_review_count": int(priority["priority_band"].eq("critical").sum()),
        "mean_response_priority_score": float(priority["response_priority_score"].mean()),
    }


def _band(score: float) -> str:
    if score >= 0.78:
        return "critical"
    if score >= 0.62:
        return "urgent"
    if score >= 0.42:
        return "elevated"
    return "routine"


def _window(score: float) -> str:
    if score >= 0.78:
        return "same_day_engineering_and_water_quality_review"
    if score >= 0.62:
        return "within_24_hours"
    if score >= 0.42:
        return "within_72_hours"
    return "routine_monitoring_cycle"


def _action(risk_type: str, score: float) -> str:
    prefix = {
        "leak": "inspect pressure/flow telemetry and nearby pipe segments",
        "contamination": "review water-quality trend, sampling plan, and affected-zone context",
        "sensor_fault": "validate calibration, battery, data gaps, and sensor replacement need",
    }.get(risk_type, "review anomaly evidence")
    return f"{prefix}; priority score {score:.2f}; qualified utility review required"
