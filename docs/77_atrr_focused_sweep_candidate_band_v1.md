# ATRR Focused Sweep Candidate Band v1

## Scope

This document records the first focused conservative `ATRR` sweep after the initial simulator proof-of-direction run.

Primary sweep summary artifacts:

- `artifacts/diagnostics/atrr_offline_simulator_focused_sweep/focused_sweep_summary.csv`
- `artifacts/diagnostics/atrr_offline_simulator_focused_sweep/FOCUSED_SWEEP_SUMMARY.md`

Observed baseline:

- `artifacts/diagnostics/lsf_v7_resonance_distribution_v2/resonance_distribution_diagnostic_summary.csv`

## Sweep Grid

The focused sweep fixed:

- `frame_smoothness_weight = 0.30`

and searched:

- `core_step_size in {0.50, 0.55}`
- `off_core_step_size in {0.10, 0.15}`
- `max_bin_step in {0.0070, 0.0085, 0.0100}`

## Main Result

The focused sweep now narrows the practical `ATRR` candidate band.

The best-balanced rows all share:

- `off_core_step_size = 0.15`
- `max_bin_step` in the range `0.0085` to `0.0100`

The difference between:

- `core_step_size = 0.50`
- `core_step_size = 0.55`

is negligible at the pack-summary level in this simulator.

## Top Configs

### 1. `c050_o015_s030_m0010`

- `shift = 55.38`
- `coverage = 63.14`
- `penalty = 32.60`
- `frame improvement = 0.007472`

Relative to observed `v7`:

- `shift delta = +16.98`
- `coverage delta = +16.86`
- `penalty delta = +6.40`
- `frame improvement delta = +0.012198`

### 2. `c055_o015_s030_m0010`

- `shift = 55.36`
- `coverage = 63.06`
- `penalty = 32.59`
- `frame improvement = 0.007485`

Relative to observed `v7`:

- `shift delta = +16.97`
- `coverage delta = +16.78`
- `penalty delta = +6.38`
- `frame improvement delta = +0.012211`

### 3. `c050_o015_s030_m00085`

- `shift = 55.05`
- `coverage = 60.67`
- `penalty = 31.39`
- `frame improvement = 0.007107`

Relative to observed `v7`:

- `shift delta = +16.66`
- `coverage delta = +14.39`
- `penalty delta = +5.19`
- `frame improvement delta = +0.011833`

## Reading Of The Result

The sweep supports four practical conclusions.

### 1. `off_core_step_size = 0.15` is preferred

The `0.15` setting consistently outperforms `0.10` on the combined tradeoff:

- better shift
- better frame improvement
- acceptable penalty growth

### 2. `core_step_size` is currently a weak control

At least in the tested range:

- `0.50`
- `0.55`

produce nearly identical pack summaries.

That means the current simulator is not especially sensitive to this knob yet.

### 3. `max_bin_step` remains the first active control

The best overall tradeoff sits at:

- `0.0085`
- or `0.0100`

while:

- `0.0070`

is a valid lower-intensity fallback when a lower localization penalty is prioritized more strongly than coverage.

### 4. The current `ATRR` candidate band is strong enough to justify reconstruction planning

The focused sweep no longer only says:

- the method family is promising in principle

It now says something narrower and more actionable:

- there is a stable conservative parameter band that still clearly outperforms the observed `LSF v7` processed result

## Recommended Candidate Band

The current recommended reconstruction-facing candidate band is:

- `core_step_size = 0.50` to `0.55`
- `off_core_step_size = 0.15`
- `frame_smoothness_weight = 0.30`
- `max_bin_step = 0.0085` to `0.0100`

Secondary fallback if the first reconstruction attempt shows too much spread or instability:

- keep `core_step_size = 0.50` to `0.55`
- keep `off_core_step_size = 0.15`
- lower `max_bin_step` to `0.0070`

## Decision

The simulator evidence is now strong enough to justify the next design step.

The project does not need another abstract simulator-only sweep before planning reconstruction.

The next step should be:

- define a conservative envelope reconstruction bridge for the recommended `ATRR` candidate band

## Immediate Next Step

The next checkpoint doc should specify:

- which synthesis-safe carrier will receive the edited envelope target
- how the edited distribution-space target will be mapped back into that carrier
- what machine-only reconstruction checks must pass before any new listening pack is built
