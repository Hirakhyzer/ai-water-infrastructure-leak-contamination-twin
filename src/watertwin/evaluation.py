"""Evaluation helpers for synthetic labels and detector outputs."""

from __future__ import annotations

import pandas as pd


def evaluate_detection(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate leak, contamination, and sensor-fault predictions using synthetic labels."""
    rows = []
    matrices = []
    tasks = [
        ("leak", "synthetic_leak_label", "predicted_leak"),
        ("contamination", "synthetic_contamination_label", "predicted_contamination"),
        ("sensor_fault", "synthetic_sensor_fault_label", "predicted_sensor_fault"),
    ]
    for name, label_col, pred_col in tasks:
        y = scores[label_col].astype(bool)
        p = scores[pred_col].astype(bool)
        tp = int((y & p).sum())
        tn = int((~y & ~p).sum())
        fp = int((~y & p).sum())
        fn = int((y & ~p).sum())
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        accuracy = (tp + tn) / max(len(scores), 1)
        rows.append({"task": name, "accuracy": round(float(accuracy), 4), "precision": round(float(precision), 4), "recall": round(float(recall), 4), "f1": round(float(f1), 4), "true_positive": tp, "false_positive": fp, "true_negative": tn, "false_negative": fn})
        matrices.extend([
            {"task": name, "actual": "positive", "predicted": "positive", "count": tp},
            {"task": name, "actual": "positive", "predicted": "negative", "count": fn},
            {"task": name, "actual": "negative", "predicted": "positive", "count": fp},
            {"task": name, "actual": "negative", "predicted": "negative", "count": tn},
        ])
    return pd.DataFrame(rows), pd.DataFrame(matrices)


def evaluation_summary(metrics: pd.DataFrame) -> dict[str, float | int]:
    if metrics.empty:
        return {"evaluation_task_count": 0, "mean_f1": 0.0}
    return {"evaluation_task_count": int(len(metrics)), "mean_accuracy": float(metrics["accuracy"].mean()), "mean_f1": float(metrics["f1"].mean())}
