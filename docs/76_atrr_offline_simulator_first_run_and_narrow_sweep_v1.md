# ATRR Offline Simulator First Run And Narrow Sweep v1

## Scope

This document records the first actual run of the `ATRR` offline simulator and the first narrow follow-up sweep used to choose the next parameter band.

Implementation:

- `scripts/simulate_targetward_resonance_residual.py`

Primary outputs:

- `artifacts/diagnostics/atrr_offline_simulator_v1/atrr_offline_simulation_summary.csv`
- `artifacts/diagnostics/atrr_offline_simulator_v1/ATRR_OFFLINE_SIMULATION_SUMMARY.md`

Sweep outputs:

- `artifacts/diagnostics/atrr_offline_simulator_sweep/c045_o010_s020_m0015/`
- `artifacts/diagnostics/atrr_offline_simulator_sweep/c055_o010_s025_m0015/`
- `artifacts/diagnostics/atrr_offline_simulator_sweep/c055_o015_s030_m0015/`
- `artifacts/diagnostics/atrr_offline_simulator_sweep/c060_o015_s035_m0015/`
- `artifacts/diagnostics/atrr_offline_simulator_sweep/c045_o010_s020_m0010/`
- `artifacts/diagnostics/atrr_offline_simulator_sweep/c055_o015_s030_m0010/`
- `artifacts/diagnostics/atrr_offline_simulator_sweep/c055_o015_s030_m0007/`

Observed baseline for comparison:

- `artifacts/diagnostics/lsf_v7_resonance_distribution_v2/resonance_distribution_diagnostic_summary.csv`

## Default Simulator Run

The first default run used:

- `core_step_size = 0.70`
- `off_core_step_size = 0.20`
- `frame_smoothness_weight = 0.30`
- `max_bin_step = 0.020`

Pack-level comparison against the observed `LSF v7` processed result:

- `shift score`
  - observed `38.39`
  - simulated `58.42`
  - delta `+20.03`
- `core coverage`
  - observed `46.28`
  - simulated `69.42`
  - delta `+23.14`
- `localization penalty`
  - observed `26.20`
  - simulated `35.57`
  - delta `+9.37`
- `context consistency`
  - observed `44.74`
  - simulated `99.96`
  - delta `+55.22`
- `frame improvement mean`
  - observed `-0.004726`
  - simulated `0.011298`
  - delta `+0.016024`

## Reading Of The Default Result

The default simulator run is directionally strong enough to clear the first method-family question:

- the `ATRR` edit object moves the score profile in the intended direction
- frame improvement becomes clearly positive
- core coverage rises materially

This means the new edit object is worth continued machine-only work.

However, the default run also looks optimistic rather than directly reconstruction-ready:

- `context_consistency_score` saturates near `100`
- the improvement is much stronger than the observed `v7` processed result on every row

This should be treated as an upper-bound directional check, not a final operating point.

## Narrow Sweep Result

The first narrow sweep tested lower step sizes and lower per-bin caps.

The most useful finding is:

- `max_bin_step` is the main active control in the current simulator

Evidence:

- changing `core_step_size` from `0.45` to `0.55` with the same `max_bin_step = 0.015` changed pack metrics only slightly
- lowering `max_bin_step` from `0.015` to `0.010` and then `0.007` changed the score profile more materially

Representative comparison:

- `c055_o015_s030_m0010`
  - shift `55.36`
  - coverage `63.06`
  - penalty `32.59`
  - frame improvement `0.007485`
- `c055_o015_s030_m0007`
  - shift `54.73`
  - coverage `57.61`
  - penalty `30.10`
  - frame improvement `0.006714`

Both remain clearly better than observed `v7`, but they are less extreme than the default run.

## Practical Constraint Update

The current simulator definition is now good enough to choose a narrow next search band.

The next sweep should focus first on:

- `max_bin_step` in the approximate range `0.007` to `0.010`

with a smaller secondary sweep around:

- `core_step_size` in the approximate range `0.50` to `0.60`
- `off_core_step_size` in the approximate range `0.10` to `0.15`
- `frame_smoothness_weight` near `0.25` to `0.35`

## Important Reading Constraint

At the current simulator stage:

- `context_consistency_score` is saturated for all tested settings

That means it is not currently useful for choosing among nearby `ATRR` simulator settings.

The near-term selection signal should therefore prioritize:

- shift improvement
- core coverage
- localization penalty
- frame improvement mean

## Immediate Next Step

Before any envelope reconstruction work, run one more focused sweep around:

- `max_bin_step = 0.007` to `0.010`
- moderate `core_step_size` and `off_core_step_size`

Then choose a small candidate band for any future reconstruction-facing implementation.
