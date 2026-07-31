# Synthetic lab

The synthetic lab creates fictional utility telemetry without requiring real utility data.

Default simulation:

- 18 zones
- 72 sensors
- 72 hours of readings
- pressure, flow, turbidity, chlorine, pH, and conductivity readings
- leak-like pressure/flow events
- contamination-like quality events
- sensor-fault-like missing/noisy events

Example:

```bash
python scripts/run_synthetic_water_lab.py --zones 30 --sensors 120 --hours 96 --seed 42
```

Generated files are written under `outputs/` and are ignored by git.
