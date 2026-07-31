"""Leak, contamination, and sensor-fault detection scoring."""

from __future__ import annotations

import pandas as pd


def score_water_anomalies(features: pd.DataFrame, leak_threshold: float = 0.50, contamination_threshold: float = 0.48, fault_threshold: float = 0.55) -> pd.DataFrame:
    """Create transparent synthetic anomaly scores and predictions."""
    df = features.copy()
    df["leak_risk_score"] = (
        0.36 * df["pressure_drop_score"]
        + 0.28 * df["flow_surge_score"]
        + 0.18 * df["pipe_age_index"]
        + 0.10 * df["missing_data_score"]
        + 0.08 * df["critical_customer_index"]
    ).clip(0, 1).round(4)
    df["contamination_risk_score"] = (
        0.42 * df["water_quality_shift_score"]
        + 0.16 * df["turbidity_spike_score"]
        + 0.16 * df["chlorine_drop_score"]
        + 0.12 * df["ph_shift_score"]
        + 0.08 * df["conductivity_shift_score"]
        + 0.06 * df["critical_customer_index"]
    ).clip(0, 1).round(4)
    df["sensor_fault_risk_score"] = (
        0.58 * df["sensor_fault_score"]
        + 0.22 * df["missing_data_score"]
        + 0.10 * (df["pressure_drop_score"] - df["flow_surge_score"]).abs()
        + 0.10 * (1 - df["service_equity_index"])
    ).clip(0, 1).round(4)
    df["predicted_leak"] = df["leak_risk_score"] >= leak_threshold
    df["predicted_contamination"] = df["contamination_risk_score"] >= contamination_threshold
    df["predicted_sensor_fault"] = df["sensor_fault_risk_score"] >= fault_threshold
    df["top_risk_type"] = df[["leak_risk_score", "contamination_risk_score", "sensor_fault_risk_score"]].idxmax(axis=1).str.replace("_risk_score", "", regex=False)
    df["overall_response_risk_score"] = df[["leak_risk_score", "contamination_risk_score", "sensor_fault_risk_score"]].max(axis=1).round(4)
    df["decision_boundary"] = "planning and engineering review signal only; not drinking-water safety certification"
    return df.sort_values("overall_response_risk_score", ascending=False).reset_index(drop=True)


def detection_summary(scores: pd.DataFrame) -> dict[str, int | float]:
    if scores.empty:
        return {"high_water_anomaly_count": 0, "mean_overall_response_risk_score": 0.0}
    return {
        "predicted_leak_count": int(scores["predicted_leak"].sum()),
        "predicted_contamination_count": int(scores["predicted_contamination"].sum()),
        "predicted_sensor_fault_count": int(scores["predicted_sensor_fault"].sum()),
        "high_water_anomaly_count": int((scores["overall_response_risk_score"] >= 0.60).sum()),
        "mean_overall_response_risk_score": float(scores["overall_response_risk_score"].mean()),
    }
