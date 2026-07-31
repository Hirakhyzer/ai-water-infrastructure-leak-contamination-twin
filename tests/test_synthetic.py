from watertwin.synthetic import SyntheticWaterConfig, generate_synthetic_water_data


def test_synthetic_generator_returns_expected_tables():
    data = generate_synthetic_water_data(SyntheticWaterConfig(zones=8, sensors=16, hours=24, seed=7))
    assert set(data) == {"zones", "pipes", "tanks", "pumps", "sensors", "readings"}
    assert len(data["zones"]) == 8
    assert len(data["sensors"]) == 16
    assert len(data["readings"]) == 16 * 24
    assert {"synthetic_leak_label", "synthetic_contamination_label", "synthetic_sensor_fault_label"}.issubset(data["readings"].columns)


def test_synthetic_network_has_pipes_and_assets():
    data = generate_synthetic_water_data(SyntheticWaterConfig(zones=10, sensors=20, hours=12, seed=9))
    assert len(data["pipes"]) >= 10
    assert len(data["tanks"]) >= 2
    assert len(data["pumps"]) >= 3
