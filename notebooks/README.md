# Notebook guidance

Run the synthetic pipeline first, then use notebooks to explore generated CSV files.

Suggested analysis:

1. Load `outputs/results/synthetic_anomaly_scores.csv`.
2. Compare leak, contamination, and sensor-fault risk distributions.
3. Inspect the highest response-priority zones.
4. Compare robustness stressors.
5. Review synthetic detector metrics.

Do not upload real utility telemetry, customer records, precise network maps, public-health incident data, or SCADA exports into notebooks unless proper authorization and governance are in place.
