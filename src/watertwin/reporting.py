"""Markdown report generation for the synthetic water digital twin."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_report(path: str | Path, summary: dict, scores: pd.DataFrame, priority: pd.DataFrame, robustness: pd.DataFrame, metrics: pd.DataFrame) -> None:
    """Write a compact engineering-review report."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    top_scores = scores.head(10)[["sensor_id", "zone_id", "top_risk_type", "overall_response_risk_score", "leak_risk_score", "contamination_risk_score", "sensor_fault_risk_score"]]
    top_priority = priority.head(10)[["sensor_id", "zone_id", "zone_type", "priority_band", "response_priority_score", "review_window"]]
    robust = robustness.sort_values("mean_score_degradation", ascending=False).head(10)
    content = [
        "# Synthetic Water Infrastructure Leak and Contamination Digital Twin Report",
        "",
        "> This report uses fictional synthetic telemetry. It supports planning and engineering review only and must not be treated as public-health advice, drinking-water certification, emergency instruction, or utility operating software.",
        "",
        "## Summary",
        "",
        _dict_table(summary),
        "",
        "## Highest anomaly scores",
        "",
        top_scores.to_markdown(index=False),
        "",
        "## Highest response priorities",
        "",
        top_priority.to_markdown(index=False),
        "",
        "## Robustness stress tests",
        "",
        robust.to_markdown(index=False),
        "",
        "## Synthetic detector metrics",
        "",
        metrics.to_markdown(index=False),
        "",
        "## Governance note",
        "",
        "Real water-system decisions require calibrated field instruments, certified laboratory sampling, utility engineers, public-health authorities, validated hydraulic models, chain-of-custody, and formal incident procedures.",
    ]
    path.write_text("\n".join(content), encoding="utf-8")


def _dict_table(summary: dict) -> str:
    return pd.DataFrame([{"metric": key, "value": value} for key, value in summary.items()]).to_markdown(index=False)
