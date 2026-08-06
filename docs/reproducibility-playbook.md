# Reproducibility Playbook

This playbook defines how to run, document, and interpret experiments from the **AI Water Infrastructure Leak and Contamination Digital Twin**.

## Minimum run record

Every experiment should record:

| Field | Example |
|---|---|
| Run name | `water_twin_seed_42_zones_30` |
| Dataset type | synthetic fictional water utility network |
| Number of zones | `30` |
| Number of sensors | `120` |
| Time horizon | `96` hours |
| Random seed | `42` |
| Event types | leak-like, contamination-like, sensor-fault-like |
| Robustness settings | missing pressure, noisy flow, quality noise, dropout, drift |
| Metrics | precision, recall, F1, confusion matrix, response-priority distribution |
| Output directory | `outputs/` |
| Boundary statement | synthetic planning-support signals only, not water-safety certification |

## Recommended command

```bash
python scripts/run_synthetic_water_lab.py --zones 30 --sensors 120 --hours 96 --seed 42
```

## Evidence bundle

A complete run should include:

```text
outputs/results/synthetic_water_zones.csv
outputs/results/synthetic_pipe_network.csv
outputs/results/synthetic_tanks.csv
outputs/results/synthetic_pumps.csv
outputs/results/synthetic_sensors.csv
outputs/results/synthetic_sensor_readings.csv
outputs/results/synthetic_water_features.csv
outputs/results/synthetic_anomaly_scores.csv
outputs/results/synthetic_robustness_tests.csv
outputs/results/synthetic_response_priorities.csv
outputs/results/synthetic_detection_metrics.csv
outputs/results/synthetic_confusion_matrix.csv
outputs/results/synthetic_water_twin_summary.json
outputs/reports/synthetic_water_infrastructure_report.md
outputs/audit/water_infrastructure_audit_log.jsonl
outputs/figures/
```

## Interpretation rules

- Report leak-like, contamination-like, and sensor-fault-like signals separately.
- Do not describe synthetic scores as measured real-world contamination.
- Report robustness degradation when sensors are missing, noisy, or drifting.
- Keep response-priority rankings as engineering review prompts, not action orders.
- Preserve the audit log when sharing results.

## Checklist before sharing results

- [ ] Seed and configuration recorded.
- [ ] Synthetic-data boundary stated clearly.
- [ ] Detection classes and assumptions documented.
- [ ] Robustness tests included.
- [ ] Figures and report attached.
- [ ] No public-health, regulatory, or SCADA-control claim is made.
