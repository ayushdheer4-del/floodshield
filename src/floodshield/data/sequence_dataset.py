"""Leakage-safe windowed samples for STG-Mamba.

For a sample date t (last day of the past window):
- x_past   [L, N, F]  normalised dynamic features for days t-L+1..t
- x_future [H, N, 1]  normalised rain for days t+1..t+H (same transform as the
                       prcp channel). Mode "observed" uses real IMD rain as a
                       stand-in for a forecast.
- static   [N, S]
- y        [H, N]      normalised log1p streamflow for t+1..t+H (0 where missing)
- mask     [H, N]      1 = observed target, 0 = missing (never filled)

A sample belongs to a split only if ALL its target days lie inside that
split's period; the past window may reach into earlier years. Samples whose
targets are all missing are skipped. Windows are views into [T, N, F]
tensors (indexing, not copying).
"""

import logging
from collections.abc import Mapping

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

log = logging.getLogger(__name__)

FUTURE_RAIN_MODES = ("observed", "noisy")


def sample_indices(dates: pd.DatetimeIndex, mask: np.ndarray, start: str, end: str,
                   window_days: int, horizon_days: int) -> np.ndarray:
    """Positions t in ``dates`` whose targets t+1..t+H all lie in [start, end],
    whose past window fits in the array, and with at least one observed target.
    ``mask`` is [T, N] (1 = observed)."""
    dates = pd.DatetimeIndex(dates)
    t = np.arange(window_days - 1, len(dates) - horizon_days)
    first_target, last_target = dates[t + 1], dates[t + horizon_days]
    in_split = (first_target >= pd.Timestamp(start)) & (last_target <= pd.Timestamp(end))
    t = t[np.asarray(in_split)]
    any_obs = np.array([mask[i + 1:i + 1 + horizon_days].any() for i in t], dtype=bool)
    return t[any_obs]


def announce_future_rain_mode(mode: str, noisy_params: Mapping | None = None) -> None:
    if mode not in FUTURE_RAIN_MODES:
        raise ValueError(f"future_rain.mode must be one of {FUTURE_RAIN_MODES}, got {mode!r}")
    banner = "#" * 72
    if mode == "observed":
        msg = ("FUTURE RAIN MODE = observed: training uses REAL observed IMD rain for "
               "days t+1..t+H as a stand-in for a rain forecast (optimistic).")
    else:
        missing = [k for k, v in (noisy_params or {}).items() if v is None]
        if missing or not noisy_params:
            raise NotImplementedError(
                "future_rain.mode = noisy is only a hook: its error parameters are not set "
                f"({missing or 'none given'}); run a forecast-error test first.")
        msg = "FUTURE RAIN MODE = noisy"
    log.debug(msg)
    print(f"{banner}\n{msg}\n{banner}", flush=True)


class WindowDataset(Dataset):
    """Samples are built by indexing shared tensors; nothing is copied per sample."""

    def __init__(self, x: np.ndarray, rain: np.ndarray, y: np.ndarray, mask: np.ndarray,
                 static: np.ndarray, dates: pd.DatetimeIndex, t_index: np.ndarray,
                 window_days: int, horizon_days: int):
        n_time = len(dates)
        if x.shape[0] != n_time or rain.shape[0] != n_time or y.shape != mask.shape:
            raise ValueError("time axes of x, rain, y and mask must match dates")
        self.x = torch.as_tensor(np.asarray(x, dtype=np.float32))            # [T, N, F]
        self.rain = torch.as_tensor(np.asarray(rain, dtype=np.float32))      # [T, N]
        self.y = torch.as_tensor(np.nan_to_num(np.asarray(y, dtype=np.float32), nan=0.0))
        self.mask = torch.as_tensor(np.asarray(mask, dtype=np.float32))      # [T, N]
        self.static = torch.as_tensor(np.asarray(static, dtype=np.float32))  # [N, S]
        self.dates = pd.DatetimeIndex(dates)
        self.t_index = np.asarray(t_index, dtype=np.int64)
        self.L, self.H = int(window_days), int(horizon_days)
        if len(self.t_index) and (self.t_index.min() < self.L - 1
                                  or self.t_index.max() + self.H >= n_time):
            raise ValueError("a sample window falls outside the arrays")

    def __len__(self) -> int:
        return len(self.t_index)

    def __getitem__(self, i: int) -> dict:
        t = int(self.t_index[i])
        past = slice(t - self.L + 1, t + 1)
        fut = slice(t + 1, t + 1 + self.H)
        return {
            "x_past": self.x[past],                    # [L, N, F]
            "x_future": self.rain[fut].unsqueeze(-1),  # [H, N, 1]
            "static": self.static,                     # [N, S]
            "y": self.y[fut],                          # [H, N]
            "mask": self.mask[fut],                    # [H, N]
            "t": self.dates[t].strftime("%Y-%m-%d"),
        }
