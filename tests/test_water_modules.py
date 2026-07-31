from watertwin.detection import score_water_anomalies
from watertwin.evaluation import evaluate_detection
from watertwin.features import build_water_features
from watertwin.priority import build_response_priorities
from watertwin.robustness import run_robustness_tests
from watertwin.synthetic import SyntheticWaterConfig, generate_synthetic_water_data


def _data():
    return generate_synthetic_water_data(SyntheticWaterConfig(zones=8, sensors=18, hours=30, seed=11))


def test_water_modules_return_expected_rows():
    data = _data()
    features = build_water_features(data["readings"], data["sensors"], data["zones"])
    scores = score_water_anomalies(features)
    robustness = run_robustness_tests(features, scores, seed=11)
    priority = build_response_priorities(scores, data["zones"])
    metrics, matrix = evaluate_detection(scores)

    assert len(features) == len(data["sensors"])
    assert len(scores) == len(features)
    assert len(priority) == len(scores)
    assert len(robustness) == 20
    assert len(metrics) == 3
    assert len(matrix) == 12
    assert scores["overall_response_risk_score"].between(0, 1).all()
    assert priority["response_priority_score"].between(0, 1).all()


def test_detector_outputs_required_predictions():
    data = _data()
    features = build_water_features(data["readings"], data["sensors"], data["zones"])
    scores = score_water_anomalies(features)
    assert {"predicted_leak", "predicted_contamination", "predicted_sensor_fault"}.issubset(scores.columns)
    assert scores["top_risk_type"].isin(["leak", "contamination", "sensor_fault"]).all()
