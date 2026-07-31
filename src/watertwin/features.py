"""Feature engineering for synthetic water-network telemetry."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_water_features(readings: pd.DataFrame, sensors: pd.DataFrame, zones: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly readings into sensor-level anomaly features."""
    sensor_meta = sensors.set_index("sensor_id")
    zone_meta = zones.set_index("zone_id")
    rows = []
    for sensor_id, group in readings.groupby("sensor_id", dropna=False):
        group = group.sort_values("timestamp_hour")
        zone_id = str(group["zone_id"].iloc[0])
        sensor = sensor_meta.loc[sensor_id]
        zone = zone_meta.loc[zone_id]
        pressure = group["pressure_kpa"]
        flow = group["flow_lpm"]
        turbidity = group["turbidity_ntu"]
        chlorine = group["chlorine_mg_l"]
        ph = group["ph"]
        conductivity = group["conductivity_us_cm"]
        missing_share = float(group[["pressure_kpa", "flow_lpm", "turbidity_ntu", "chlorine_mg_l", "ph"]].isna().mean().mean())
        rows.append({
            "sensor_id": sensor_id,
            "sensor_type": str(group["sensor_type"].iloc[0]),
            "zone_id": zone_id,
            "critical_customer_index": float(zone.critical_customer_index),
            "service_equity_index": float(zone.service_equity_index),
            "pipe_age_index": float(zone.pipe_age_index),
            "mean_pressure_kpa": round(float(pressure.mean(skipna=True)), 4),
            "mean_flow_lpm": round(float(flow.mean(skipna=True)), 4),
            "pressure_drop_score": round(float(_drop_score(pressure)), 4),
            "flow_surge_score": round(float(_surge_score(flow)), 4),
            "turbidity_spike_score": round(float(_zclip(turbidity)), 4),
            "chlorine_drop_score": round(float(_inverse_zclip(chlorine)), 4),
            "ph_shift_score": round(float(np.clip(abs(ph.mean(skipna=True) - 7.3) / 1.2, 0, 1)), 4),
            "conductivity_shift_score": round(float(_zclip(conductivity)), 4),
            "water_quality_shift_score": round(float(_quality_shift(turbidity, chlorine, ph, conductivity)), 4),
            "missing_data_score": round(float(np.clip(missing_share / 0.25, 0, 1)), 4),
            "sensor_fault_score": round(float(_sensor_fault_score(group, float(sensor.noise_index), int(sensor.calibration_age_days), float(sensor.battery_health))), 4),
            "synthetic_leak_label": bool(group["synthetic_leak_label"].max()),
            "synthetic_contamination_label": bool(group["synthetic_contamination_label"].max()),
            "synthetic_sensor_fault_label": bool(group["synthetic_sensor_fault_label"].max()),
        })
    return pd.DataFrame(rows)


def feature_summary(features: pd.DataFrame) -> dict[str, int | float]:
    if features.empty:
        return {"feature_record_count": 0, "mean_pressure_drop_score": 0.0}
    return {
        "feature_record_count": int(len(features)),
        "mean_pressure_drop_score": float(features["pressure_drop_score"].mean()),
        "mean_water_quality_shift_score": float(features["water_quality_shift_score"].mean()),
        "mean_sensor_fault_score": float(features["sensor_fault_score"].mean()),
    }


def _drop_score(series: pd.Series) -> float:
    clean = series.dropna()
    if clean.empty:
        return 1.0
    early = clean.head(max(3, len(clean) // 4)).median()
    late = clean.tail(max(3, len(clean) // 4)).median()
    return float(np.clip((early - late) / max(early, 1), 0, 1))


def _surge_score(series: pd.Series) -> float:
    clean = series.dropna()
    if clean.empty:
        return 1.0
    early = clean.head(max(3, len(clean) // 4)).median()
    late = clean.tail(max(3, len(clean) // 4)).median()
    return float(np.clip((late - early) / max(early, 1), 0, 1))


def _quality_shift(turbidity: pd.Series, chlorine: pd.Series, ph: pd.Series, conductivity: pd.Series) -> float:
    return float(np.clip(0.38 * _zclip(turbidity) + 0.28 * _inverse_zclip(chlorine) + 0.18 * abs(ph.mean(skipna=True) - 7.3) / 1.2 + 0.16 * _zclip(conductivity), 0, 1))


def _sensor_fault_score(group: pd.DataFrame, noise_index: float, calibration_age_days: int, battery_health: float) -> float:
    missing = float(group[["pressure_kpa", "flow_lpm", "turbidity_ntu", "chlorine_mg_l"]].isna().mean().mean())
    volatility_values = [
        group["pressure_kpa"].pct_change().abs().replace([np.inf, -np.inf], np.nan).mean(),
        group["flow_lpm"].pct_change().abs().replace([np.inf, -np.inf], np.nan).mean(),
        group["turbidity_ntu"].pct_change().abs().replace([np.inf, -np.inf], np.nan).mean(),
    ]
    volatility = float(np.nanmean(volatility_values))
    if np.isnan(volatility):
        volatility = 0.0
    return float(np.clip(0.25 * missing / 0.20 + 0.25 * noise_index + 0.25 * min(calibration_age_days / 365, 1.0) + 0.15 * (1 - battery_health) + 0.10 * min(volatility, 1.0), 0, 1))


def _zclip(series: pd.Series) -> float:
    clean = series.dropna()
    if len(clean) < 3:
        return 1.0
    return float(np.clip((clean.quantile(0.90) - clean.median()) / (clean.median() + 1e-6), 0, 1))


def _inverse_zclip(series: pd.Series) -> float:
    clean = series.dropna()
    if len(clean) < 3:
        return 1.0
    med = clean.median()
    low = clean.quantile(0.10)
    return float(np.clip((med - low) / (med + 1e-6), 0, 1))
