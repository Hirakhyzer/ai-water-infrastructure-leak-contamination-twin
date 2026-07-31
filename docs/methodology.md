# Methodology

This project implements a transparent synthetic baseline for water-infrastructure anomaly review.

The pipeline creates fictional zones, pipes, tanks, pumps, sensors, and telemetry. It injects synthetic leak-like pressure and flow changes, contamination-like water-quality changes, and sensor-fault-like missing/noisy readings. It then aggregates telemetry into interpretable features and scores leak, contamination, and sensor-fault risk separately.

The scoring approach is intentionally simple and auditable. It is a research baseline for planning support, not a certified hydraulic model, laboratory method, regulatory method, or public-health decision tool.

## Main stages

1. Generate a fictional water distribution network.
2. Simulate hourly pressure, flow, turbidity, chlorine, pH, and conductivity readings.
3. Extract pressure-drop, flow-surge, quality-shift, missing-data, and sensor-fault features.
4. Score leak-like, contamination-like, and sensor-fault-like risks.
5. Stress test score stability under missing/noisy sensors.
6. Rank response priorities for human engineering and water-quality review.
7. Write CSV, JSON, figures, report, and hash-chained audit log.
