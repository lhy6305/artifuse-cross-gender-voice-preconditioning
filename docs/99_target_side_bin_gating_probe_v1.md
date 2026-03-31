# Target Side Bin Gating Probe v1

## Summary

This checkpoint records the first route-worthy result from moving stabilization
upstream into target-side selective edit gating.

The new idea is not another backend rescue layer.

Instead, it keeps the current `anchor075` BigVGAN backend stack and gates the
target edit before carrier synthesis:

- only keep bin edits whose utterance-level target delta is large enough
- and whose prototype occupancy is not too low

This is the first post-human-review move on the active route that reduces
structure risk materially without collapsing the whole pack.

## New Control

`scripts/run_atrr_vocoder_carrier_adapter.py` now supports target-side bin
gating through:

- `--target-bin-delta-threshold`
- `--target-bin-delta-threshold-masculine`
- `--target-bin-delta-threshold-feminine`
- `--target-bin-occupancy-threshold`

The gate acts before backend-domain target mel synthesis.

Low-signal bins are reverted to the source frame distribution instead of being
passed through as edited bins.

## Global Bin Gate Sweep

The first sweep tested:

1. delta `0.010`, occupancy `0.05`
2. delta `0.015`, occupancy `0.05`
3. delta `0.020`, occupancy `0.05`

All runs kept:

- `frame_distribution_anchor_alpha = 0.75`
- `voiced_target_blend_alpha = 0.75`
- pitch correction trigger `150`
- pitch correction cap `200`

Outputs:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v6_target_bin_gating_sweep_plus010/`

## Global Sweep Reading

Baseline `anchor075`:

- shift: `45.10`
- target probe structure risk: `45.76`
- edit-added structure risk: `24.63`

Global delta `0.010`:

- shift: `38.72`
- target probe structure risk: `36.62`
- edit-added structure risk: `15.49`

Global delta `0.015`:

- shift: `39.73`
- target probe structure risk: `35.61`
- edit-added structure risk: `14.48`

Global delta `0.020`:

- shift: `38.15`
- target probe structure risk: `35.45`
- edit-added structure risk: `14.32`

Reading:

- target-side bin gating is a real route improvement
- it reduces structure risk much more efficiently than the earlier selective
  frame-anchor attempt
- but the best global threshold still shows a cross-direction tradeoff

## Why A Hybrid Threshold Was Tested

The global sweep split by direction:

- `female -> masculine` benefited more from the looser `0.010` threshold
- `male -> feminine` benefited more from the tighter `0.015` threshold

This suggested that the next useful test was a direction-conditioned threshold
rather than another single global value.

## Hybrid Result

Hybrid setting:

- masculine delta threshold `0.010`
- feminine delta threshold `0.015`
- occupancy threshold `0.05`

Output:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v7_target_bin_gating_hybrid/`

Pack summary:

- shift: `41.65`
- target log-mel MAE: `0.5445`
- target probe structure risk: `36.40`
- edit-added structure risk: `15.26`

Compared with the old `anchor075` baseline:

- shift: `45.10 -> 41.65`
- target probe structure risk: `45.76 -> 36.40`
- edit-added structure risk: `24.63 -> 15.26`

This is a materially better balance than the old baseline.

## Important Row Level Reading

`p241_005_mic1`:

- baseline shift: `28.49`
- hybrid shift: `25.80`
- baseline target risk: `41.22`
- hybrid target risk: `24.06`

This row keeps most of its movement while becoming far more stable.

`p230_107_mic1`:

- baseline shift: `20.53`
- hybrid shift: `36.37`
- baseline target risk: `62.95`
- hybrid target risk: `65.75`

This row still remains structurally unsafe, but the hybrid gate at least
recovers movement instead of collapsing it.

`2086_149214_000006_000002`:

- baseline shift: `64.58`
- hybrid shift: `37.87`
- baseline target risk: `60.31`
- hybrid target risk: `57.99`

This is still the main cost of the new gate.

## Route Decision

- Keep the ATRR target package family open.
- Replace plain `anchor075` with the direction-conditioned target-bin gate as
  the new active machine-only BigVGAN baseline.
- Do not send this new stack to human review yet.

Reason:

- structure improves materially enough to justify the new baseline
- but remaining high-risk rows still make another human pass premature

## Immediate Next Step

The next step should stay target-side and selective:

1. keep the new hybrid target-bin gate as the machine baseline
2. focus on the remaining high-risk rows, especially `p230_107_mic1` and
   `2086_149214_000006_000002`
3. test whether the gate should vary by `f0` bucket or by utterance-level edit
   strength before the next human review
