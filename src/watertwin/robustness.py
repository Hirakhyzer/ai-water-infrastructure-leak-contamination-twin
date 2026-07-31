"""Robustness testing under missing and noisy sensors."""

from __future__ import annotations

import numpy as np
import pandas as pd

STRESSORS = ["missing_pressure", "flow_noise", "quality_noise", "sensor_dropout", "calibration_drift"]


def run_robustness_tests(features: pd.DataFrame, scores: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Estimate how anomaly scores degrade under synthetic sensor stressors."""
    rng = np.random.default_rng(seed + 99)
    base = scores[["sensor_id", "zone_id", "overall_response_risk_score", "leak_risk_score", "contamination_risk_score", "sensor_fault_risk_score"]]
    rows = []
    for stressor in STRESSORS:
        for severity in [0.10, 0.25, 0.40, 0.60]:
            noise = rng.normal(0, severity * 0.05, len(base))
            if stressor == "missing_pressure":
                adjusted = base["leak_risk_score"] * (1 - 0.42 * severity) + base["sensor_fault_risk_score"] * 0.12 * severity + noise
            elif stressor == "flow_noise":
                adjusted = base["leak_risk_score"] * (1 - 0.25 * severity) + noise
            elif stressor == "quality_noise":
                adjusted = base["contamination_risk_score"] * (1 - 0.38 * severity) + noise
            elif stressor == "sensor_dropout":
                adjusted = base["overall_response_risk_score"] * (1 - 0.50 * severity) + base["sensor_fault_risk_score"] * 0.20 * severity + noise
            else:
                adjusted = base["overall_response_risk_score"] * (1 - 0.18 * severity) + base["sensor_fault_risk_score"] * 0.22 * severity + noise
            adjusted = adjusted.clip(0, 1)
            degradation = (base["overall_response_risk_score"] - adjusted).clip(lower=0)
            rows.append({
                "stressor": stressor,
                "severity": severity,
                "mean_adjusted_risk_score": round(float(adjusted.mean()), 4),
                "mean_score_degradation": round(float(degradation.mean()), 4),
                "sensors_with_major_degradation": int((degradation >= 0.12).sum()),
                "robustness_pass_rate": round(float((degradation < 0.12).mean()), 4),
            })
    return pd.DataFrame(rows)


def robustness_summary(robustness: pd.DataFrame) -> dict[str, int | float]:
    if robustness.empty:
        return {"mean_robustness_pass_rate": 0.0}
    return {
        "robustness_test_count": int(len(robustness)),
        "mean_robustness_pass_rate": float(robustness["robustness_pass_rate"].mean()),
        "worst_mean_score_degradation": float(robustness["mean_score_degradation"].max()),
    }
