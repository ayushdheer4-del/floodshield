# Frontend (stack TO BE DECIDED)

No framework has been chosen or scaffolded yet. Do not run `npm init` until
the stack is decided.

## Planned features

- Basin selector (Godavari / Mahanadi)
- Map of gauges, coloured by alert status (predicted flow above the gauge's
  own high-flow threshold; not an official CWC warning level)
- Per-gauge daily forecast chart for the next 4 days, with the threshold line
- Clear note that this is a daily model and cannot resolve the hour
- Data-source credits: IMD (rainfall, temperature), NASA GEOS-FP (forecast
  rain, once verified), CAMELS-IND (training data). Exact attribution wording
  is TODO once each source's terms are confirmed.
- A visible "replay" label whenever a saved past event is shown instead of
  live data

Data will come from the FastAPI backend in `app/backend/` (not implemented).
