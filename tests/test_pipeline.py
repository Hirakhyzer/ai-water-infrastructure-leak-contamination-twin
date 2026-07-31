import json
import subprocess
import sys


def test_pipeline_smoke(tmp_path):
    output_dir = tmp_path / "outputs"
    result = subprocess.run(
        [sys.executable, "scripts/run_synthetic_water_lab.py", "--zones", "8", "--sensors", "18", "--hours", "24", "--seed", "13", "--output-dir", str(output_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)
    assert summary["synthetic_zone_count"] == 8
    assert summary["synthetic_sensor_count"] == 18
    assert (output_dir / "results" / "synthetic_water_twin_summary.json").exists()
    assert (output_dir / "reports" / "synthetic_water_infrastructure_report.md").exists()
    assert (output_dir / "audit" / "water_infrastructure_audit_log.jsonl").exists()
    assert (output_dir / "figures" / "synthetic_anomaly_score_distribution.png").exists()
