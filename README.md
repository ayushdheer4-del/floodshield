# FloodShield: STG-Mamba (Phase 2)

FloodShield is an AI-based flood forecasting project for Indian river basins.
This repository holds **Phase 2**: a spatio-temporal graph + Mamba (STG-Mamba)
streamflow forecasting model, plus a live prediction backend and frontend for
the project review.

> **Status: early data preparation.** Implemented so far: dataset download
> (`scripts/download_data.py`) and gauge selection (`scripts/select_gauges.py`).
> No model, graph code, weather fetching, backend endpoint or frontend exists yet.

## Methodology (three phases)

| Phase | Approach | Where |
|-------|----------|-------|
| 1 | XGBoost baseline | Separate repository (maintained separately) |
| 2 | **STG-Mamba primary forecasting** | **This repository** |
| 3 | XGBoost residual correction on STG-Mamba output | Planned separately (out of scope here) |

## Scope

- **Region:** India only. Two basins: **Godavari** and **Mahanadi**.
- **Time step:** daily.
- **Target:** observed river streamflow (m3/s) at gauge nodes.
- **Forecast horizon:** 1 to 3 days (**proposed**, not final).
- **Graph:** nodes = river gauges; edges = upstream to downstream links derived
  from the river network.
- **Inputs:** weather + static catchment attributes + graph. The model is
  weather-driven and does **not** use past observed flow as input, so no live
  gauge feed is needed for live predictions.

## Datasets

| Dataset | Role |
|---------|------|
| [CAMELS-IND v2.2](https://doi.org/10.5281/zenodo.14999580) | Observed daily streamflow (targets), gauge locations, static attributes, catchment boundaries |
| [HydroRIVERS](https://www.hydrosheds.org/products/hydrorivers) | River network for upstream/downstream graph edges |
| [Open-Meteo Archive API](https://open-meteo.com/en/docs/historical-weather-api) | Historical (ERA5-based) weather at each gauge for training |
| [Open-Meteo Forecast API](https://open-meteo.com/en/docs) | Live recent + forecast weather for live predictions |

CAMELS-IND contains 50 Godavari (CWC basin code `03`) and 19 Mahanadi (`08`)
gauges. The gauges selected for training are listed in
[configs/selected_gauges.csv](configs/selected_gauges.csv), produced by
`scripts/select_gauges.py` from the PROPOSED thresholds in `configs/data.yaml`.
See [docs/dataset_sources.md](docs/dataset_sources.md) for details, licensing
and limitations.

Weather data by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0).

## Compute

Developed on an Apple M4 Pro (macOS arm64, no CUDA). PyTorch's **MPS** backend
(Apple GPU, float32) is the primary device; CPU is a logged fallback only.

## Setup

Requires Python 3.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
cp .env.example .env
```

## Data preparation

```bash
python scripts/download_data.py   # CAMELS-IND + HydroRIVERS into data/raw/ (verified, re-runnable)
python scripts/select_gauges.py   # writes configs/selected_gauges.csv and outputs/gauge_selection_report.csv
```

## Run tests

```bash
source .venv/bin/activate
pytest
```

`tests/test_environment.py` checks imports, MPS availability and a tiny float32
tensor op; `tests/test_data_pipeline.py` tests the loader and gauge-selection
logic. The remaining test files are skipped placeholders.

## Layout

- `configs/`: YAML configs and the selected gauge list
- `data/`: raw / processed / graph data (never committed)
- `src/floodshield/`: the Python package
- `scripts/`: command-line entry points
- `app/backend/`: FastAPI live-demo backend (placeholder)
- `app/frontend/`: frontend (stack to be decided)
- `docs/`: dataset sources, model architecture, live demo plan
