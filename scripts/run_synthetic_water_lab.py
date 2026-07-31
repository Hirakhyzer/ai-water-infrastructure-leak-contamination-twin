"""Run the independent synthetic water infrastructure leak and contamination digital twin.

The command uses only fictional zones, pipes, tanks, pumps, sensors, and telemetry.
It demonstrates leak-risk detection, contamination anomaly detection, sensor-fault
separation, robustness testing under missing/noisy sensors, response-priority
scoring, reporting, figures, evaluation metrics, and a hash-chained audit log.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from watertwin.audit import append_record, verify_log
from watertwin.config import ensure_output_dirs, set_seed
from watertwin.detection import detection_summary, score_water_anomalies
from watertwin.evaluation import evaluate_detection, evaluation_summary
from watertwin.features import build_water_features, feature_summary
from watertwin.priority import build_response_priorities, priority_summary
from watertwin.reporting import write_report
from watertwin.robustness import robustness_summary, run_robustness_tests
from watertwin.synthetic import SyntheticWaterConfig, generate_synthetic_water_data
from watertwin.visualization import (
    plot_anomaly_scores,
    plot_evaluation,
    plot_priority_bands,
    plot_quality_shift,
    plot_robustness,
    plot_zone_risk,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic water infrastructure leak and contamination digital twin.")
    parser.add_argument("--zones", type=int, default=18)
    parser.add_argument("--sensors", type=int, default=72)
    parser.add_argument("--hours", type=int, default=72)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    data = generate_synthetic_water_data(SyntheticWaterConfig(zones=args.zones, sensors=args.sensors, hours=args.hours, seed=args.seed))
    zones = data["zones"]
    pipes = data["pipes"]
    tanks = data["tanks"]
    pumps = data["pumps"]
    sensors = data["sensors"]
    readings = data["readings"]

    features = build_water_features(readings, sensors, zones)
    scores = score_water_anomalies(features)
    robustness = run_robustness_tests(features, scores, seed=args.seed)
    priority = build_response_priorities(scores, zones)
    metrics, matrix = evaluate_detection(scores)

    summary = {
        "seed": args.seed,
        "synthetic_zone_count": int(len(zones)),
        "synthetic_pipe_count": int(len(pipes)),
        "synthetic_sensor_count": int(len(sensors)),
        "synthetic_reading_count": int(len(readings)),
        "data_origin": "synthetic fictional water-network telemetry",
        "decision_boundary": "planning support only; not public-health advice, utility control, emergency response, or drinking-water certification",
    }
    summary.update(feature_summary(features))
    summary.update(detection_summary(scores))
    summary.update(robustness_summary(robustness))
    summary.update(priority_summary(priority))
    summary.update(evaluation_summary(metrics))

    zones.to_csv(outputs["results"] / "synthetic_water_zones.csv", index=False)
    pipes.to_csv(outputs["results"] / "synthetic_pipe_network.csv", index=False)
    tanks.to_csv(outputs["results"] / "synthetic_tanks.csv", index=False)
    pumps.to_csv(outputs["results"] / "synthetic_pumps.csv", index=False)
    sensors.to_csv(outputs["results"] / "synthetic_sensors.csv", index=False)
    readings.to_csv(outputs["results"] / "synthetic_sensor_readings.csv", index=False)
    features.to_csv(outputs["results"] / "synthetic_water_features.csv", index=False)
    scores.to_csv(outputs["results"] / "synthetic_anomaly_scores.csv", index=False)
    robustness.to_csv(outputs["results"] / "synthetic_robustness_tests.csv", index=False)
    priority.to_csv(outputs["results"] / "synthetic_response_priorities.csv", index=False)
    metrics.to_csv(outputs["results"] / "synthetic_detection_metrics.csv", index=False)
    matrix.to_csv(outputs["results"] / "synthetic_confusion_matrix.csv", index=False)

    audit_path = outputs["audit"] / "water_infrastructure_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "independent synthetic water-infrastructure planning support only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_water_twin_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_water_infrastructure_report.md", summary, scores, priority, robustness, metrics)
    plot_anomaly_scores(scores, outputs["figures"] / "synthetic_anomaly_score_distribution.png")
    plot_zone_risk(priority, outputs["figures"] / "synthetic_zone_response_priority.png")
    plot_quality_shift(scores, outputs["figures"] / "synthetic_water_quality_shift.png")
    plot_robustness(robustness, outputs["figures"] / "synthetic_sensor_robustness.png")
    plot_evaluation(metrics, outputs["figures"] / "synthetic_detection_metrics.png")
    plot_priority_bands(priority, outputs["figures"] / "synthetic_priority_bands.png")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
