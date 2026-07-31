"""Synthetic water-distribution network generator.

All records are fictional and intended for water-infrastructure research only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

ZONE_TYPES = ["residential", "commercial", "industrial", "hospital", "school", "mixed"]
PIPE_MATERIALS = ["ductile_iron", "PVC", "steel", "cast_iron", "HDPE"]
SENSOR_TYPES = ["pressure", "flow", "quality", "tank", "pump"]


@dataclass(frozen=True)
class SyntheticWaterConfig:
    """Configuration for a synthetic water-network experiment."""
    zones: int = 18
    sensors: int = 72
    seed: int = 42
    hours: int = 72


def generate_synthetic_water_data(config: SyntheticWaterConfig) -> dict[str, pd.DataFrame]:
    """Generate zones, pipes, tanks, pumps, sensors, and hourly telemetry."""
    rng = np.random.default_rng(config.seed)
    zones = _zones(config.zones, rng)
    pipes = _pipes(zones, rng)
    tanks = _tanks(zones, rng)
    pumps = _pumps(zones, rng)
    sensors = _sensors(zones, pipes, config.sensors, rng)
    readings = _readings(zones, pipes, sensors, config.hours, rng)
    return {"zones": zones, "pipes": pipes, "tanks": tanks, "pumps": pumps, "sensors": sensors, "readings": readings}


def _zones(count: int, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for idx in range(count):
        zone_type = str(rng.choice(ZONE_TYPES, p=[0.38, 0.16, 0.12, 0.08, 0.10, 0.16]))
        population = int(rng.integers(850, 12500))
        criticality = {"hospital": 0.95, "school": 0.75, "industrial": 0.68, "commercial": 0.56, "mixed": 0.62, "residential": 0.50}[zone_type]
        rows.append({
            "zone_id": f"Z{idx + 1:03d}",
            "zone_name": f"Synthetic District {idx + 1}",
            "zone_type": zone_type,
            "population": population,
            "critical_customer_index": round(float(np.clip(criticality + rng.normal(0, 0.08), 0.25, 1.0)), 3),
            "pipe_age_index": round(float(rng.uniform(0.15, 0.95)), 3),
            "elevation_m": round(float(rng.uniform(12, 180)), 2),
            "baseline_demand_lpm": round(float(population * rng.uniform(0.10, 0.22)), 2),
            "service_equity_index": round(float(rng.uniform(0.25, 0.95)), 3),
        })
    return pd.DataFrame(rows)


def _pipes(zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    zone_ids = list(zones["zone_id"])
    for idx, zone_id in enumerate(zone_ids):
        rows.append(_pipe_row(idx + 1, zone_id, zone_ids[(idx + 1) % len(zone_ids)], rng))
    for _ in range(max(3, len(zone_ids) // 2)):
        start, end = rng.choice(zone_ids, size=2, replace=False)
        rows.append(_pipe_row(len(rows) + 1, str(start), str(end), rng))
    return pd.DataFrame(rows)


def _pipe_row(idx: int, start: str, end: str, rng: np.random.Generator) -> dict:
    age = int(rng.integers(2, 95))
    return {
        "pipe_id": f"P{idx:04d}",
        "from_zone": start,
        "to_zone": end,
        "material": str(rng.choice(PIPE_MATERIALS)),
        "age_years": age,
        "diameter_mm": int(rng.choice([100, 150, 200, 300, 450, 600])),
        "length_m": round(float(rng.uniform(120, 3200)), 2),
        "baseline_pressure_kpa": round(float(rng.uniform(260, 620)), 2),
        "baseline_flow_lpm": round(float(rng.uniform(450, 6800)), 2),
        "leak_prior_index": round(float(np.clip(0.18 + age / 110 + rng.normal(0, 0.10), 0.05, 1.0)), 3),
    }


def _tanks(zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    chosen = zones.sample(n=max(2, min(6, len(zones) // 3)), random_state=int(rng.integers(0, 100000)))
    rows = []
    for idx, zone in enumerate(chosen.itertuples(index=False), start=1):
        capacity = float(rng.uniform(250000, 2200000))
        rows.append({"tank_id": f"T{idx:03d}", "zone_id": zone.zone_id, "capacity_liters": round(capacity, 2), "current_level_liters": round(capacity * float(rng.uniform(0.42, 0.95)), 2), "chlorine_boost_available": bool(rng.random() > 0.22)})
    return pd.DataFrame(rows)


def _pumps(zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    chosen = zones.sample(n=max(3, min(8, len(zones) // 2)), random_state=int(rng.integers(0, 100000)))
    rows = []
    for idx, zone in enumerate(chosen.itertuples(index=False), start=1):
        rows.append({"pump_id": f"PU{idx:03d}", "zone_id": zone.zone_id, "nominal_flow_lpm": round(float(rng.uniform(1200, 8500)), 2), "availability": str(rng.choice(["online", "degraded", "maintenance"], p=[0.72, 0.20, 0.08])), "energy_risk_index": round(float(rng.uniform(0.05, 0.75)), 3)})
    return pd.DataFrame(rows)


def _sensors(zones: pd.DataFrame, pipes: pd.DataFrame, count: int, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    zone_ids = list(zones["zone_id"])
    pipe_ids = list(pipes["pipe_id"])
    for idx in range(count):
        sensor_type = str(rng.choice(SENSOR_TYPES, p=[0.28, 0.24, 0.28, 0.10, 0.10]))
        rows.append({
            "sensor_id": f"S{idx + 1:04d}",
            "sensor_type": sensor_type,
            "zone_id": str(rng.choice(zone_ids)),
            "pipe_id": str(rng.choice(pipe_ids)) if sensor_type in ["pressure", "flow"] else "",
            "calibration_age_days": int(rng.integers(3, 420)),
            "missing_rate": round(float(rng.uniform(0.0, 0.18)), 3),
            "noise_index": round(float(rng.uniform(0.01, 0.35)), 3),
            "battery_health": round(float(rng.uniform(0.25, 1.0)), 3),
        })
    return pd.DataFrame(rows)


def _readings(zones: pd.DataFrame, pipes: pd.DataFrame, sensors: pd.DataFrame, hours: int, rng: np.random.Generator) -> pd.DataFrame:
    zone_lookup = zones.set_index("zone_id")
    pipe_lookup = pipes.set_index("pipe_id")
    contaminated_zones = set(rng.choice(list(zones["zone_id"]), size=max(1, len(zones) // 7), replace=False))
    leaking_pipes = set(rng.choice(list(pipes["pipe_id"]), size=max(2, len(pipes) // 6), replace=False))
    faulty_sensors = set(rng.choice(list(sensors["sensor_id"]), size=max(2, len(sensors) // 9), replace=False))
    rows = []
    for hour in range(hours):
        daily = 1.0 + 0.20 * np.sin(2 * np.pi * (hour % 24) / 24)
        for sensor in sensors.itertuples(index=False):
            zone = zone_lookup.loc[sensor.zone_id]
            pipe = pipe_lookup.loc[sensor.pipe_id] if sensor.pipe_id else None
            is_leak = sensor.pipe_id in leaking_pipes and hour >= hours * 0.35
            is_contam = sensor.zone_id in contaminated_zones and hour >= hours * 0.45
            is_fault = sensor.sensor_id in faulty_sensors and hour >= hours * 0.25
            pressure = float((pipe.baseline_pressure_kpa if pipe is not None else 410.0) * daily + rng.normal(0, 9))
            flow = float((pipe.baseline_flow_lpm if pipe is not None else zone.baseline_demand_lpm) * daily + rng.normal(0, 60))
            turbidity = float(np.clip(0.22 + rng.normal(0, 0.05), 0.02, 5.0))
            chlorine = float(np.clip(0.82 + rng.normal(0, 0.06), 0.05, 2.2))
            ph = float(np.clip(7.35 + rng.normal(0, 0.12), 6.0, 9.0))
            conductivity = float(np.clip(420 + rng.normal(0, 30), 100, 1200))
            if is_leak:
                pressure -= float(rng.uniform(35, 115)); flow += float(rng.uniform(120, 700))
            if is_contam:
                turbidity += float(rng.uniform(0.45, 2.8)); chlorine -= float(rng.uniform(0.15, 0.52)); ph += float(rng.normal(0.25, 0.18)); conductivity += float(rng.uniform(60, 260))
            if is_fault:
                pressure += float(rng.normal(0, 45)); flow += float(rng.normal(0, 300)); turbidity += float(rng.normal(0, 0.55)); chlorine += float(rng.normal(0, 0.25))
            missing = rng.random() < float(sensor.missing_rate)
            rows.append({
                "timestamp_hour": int(hour), "sensor_id": sensor.sensor_id, "zone_id": sensor.zone_id, "pipe_id": sensor.pipe_id, "sensor_type": sensor.sensor_type,
                "pressure_kpa": np.nan if missing else round(max(0.0, pressure), 3),
                "flow_lpm": np.nan if missing else round(max(0.0, flow), 3),
                "turbidity_ntu": np.nan if missing else round(max(0.0, turbidity), 4),
                "chlorine_mg_l": np.nan if missing else round(max(0.0, chlorine), 4),
                "ph": np.nan if missing else round(ph, 4),
                "conductivity_us_cm": np.nan if missing else round(conductivity, 3),
                "synthetic_leak_label": bool(is_leak), "synthetic_contamination_label": bool(is_contam), "synthetic_sensor_fault_label": bool(is_fault),
            })
    return pd.DataFrame(rows)
