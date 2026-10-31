# STG-Mamba model architecture (intended concept)

> **Not implemented.** This describes the planned design only. Window sizes
> and the feature list are PROPOSED settings in `configs/model.yaml`.

## Concept

1. **Inputs per gauge node:**
   - a past window of daily weather (`window_days`, proposed 90) from the
     CAMELS-IND forcings: `feature_list` (default prcp, tmax, tmin, tavg from IMD);
   - future rain for the forecast days (`horizon_days`, proposed 4). In
     training this is observed IMD rain as a stand-in for a forecast
     (`configs/training.yaml` `future_rain.mode`); live it will be forecast rain;
   - static catchment attributes from CAMELS-IND (none derived from streamflow).
2. **Weather-driven:** no past observed streamflow is an input.
3. **Graph step:** information is propagated along directed upstream to
   downstream edges between gauges (from HydroRIVERS, `configs/graph_edges.csv`),
   so a downstream gauge sees the conditions of its upstream catchments.
   Implemented with plain-torch adjacency matrices (no torch-geometric).
4. **Temporal blocks:** Mamba (selective state space) blocks model the
   temporal dynamics. Pure-PyTorch implementation, no CUDA kernels.
5. **Output:** daily streamflow per gauge for days t+1..t+4 (log1p, then
   standardised per gauge with training-period statistics).
6. **Phase 3:** XGBoost trained on STG-Mamba's errors corrects systematic biases.

Training uses a masked loss so days with missing observed streamflow are
ignored; missing targets are never filled.

## Compute notes (planned, not implemented)

- **Primary device is MPS** (Apple GPU), float32 only; CPU is a logged fallback.
- The Mamba selective scan must **not** run as one tiny GPU op per time step,
  especially with a 90-day window. Plan to use a parallel (associative) scan
  or a chunked scan.
- Process all gauge nodes of both basins as one batch dimension so the GPU
  receives large tensors.
- Keep data resident on the GPU to avoid host/device transfers.
- Do not rely on `torch.compile` on MPS.
- Once the model exists, benchmark MPS vs CPU on a tiny forward/backward pass
  and report the result.
