"""Flood alerts from per-gauge high-flow thresholds (not implemented).

Thresholds are training-period streamflow percentiles per gauge
(configs/flow_thresholds.csv). An alert means predicted daily flow above the
gauge's own threshold; it is not an official CWC warning level and a daily
model cannot resolve the hour.
"""

# TODO: Apply configs/training.yaml warning.threshold_quantile and alert_margin (tuned on validation only).
