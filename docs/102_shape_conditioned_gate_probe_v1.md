# Shape Conditioned Gate Probe v1

## Summary

This checkpoint records the first target-shape-conditioned refinement on top of
the active hybrid target-bin gate.

The purpose was narrow:

- keep the current hybrid baseline
- only target the feminine outlier shape that still includes
  `2086_149214_000006_000002`
- avoid harming `p241_005_mic1`, which had already improved under the hybrid
  baseline

The tested shape key was the sum of the top-3 utterance-level target-delta bins.

Result:

- the shape-conditioned override behaves as intended
- it touches `2086` without touching `p241`
- but the gain is too small to justify a baseline change

## New Control

`scripts/run_atrr_vocoder_carrier_adapter.py` now supports:

- `--target-bin-shape-topk-count`
- `--target-bin-shape-topk-sum-cutoff`
- `--target-bin-delta-threshold-feminine-sharp`

This allows a stricter feminine target-bin gate only when the target-package
delta is sufficiently concentrated.

## Tested Variants

Baseline hybrid:

- masculine delta `0.010`
- feminine delta `0.015`
- occupancy `0.05`

Shape-conditioned variants:

1. top-3 delta-sum cutoff `0.42`, feminine sharp delta `0.020`
2. top-3 delta-sum cutoff `0.45`, feminine sharp delta `0.020`

Outputs:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v10_shape_conditioned_gate/`

## Pack Level Result

Hybrid baseline:

- shift: `41.65`
- target probe structure risk: `36.40`
- edit-added structure risk: `15.26`

Shape-conditioned variants:

- shift: `41.69`
- target probe structure risk: `36.36`
- edit-added structure risk: `15.23`

Reading:

- the effect is directionally correct
- but it is extremely small at the pack level
- both tested cutoffs collapse to the same practical behavior on fixed8

## Important Row Level Reading

`2086_149214_000006_000002`:

- hybrid shift: `37.87`
- shape-conditioned shift: `38.16`
- hybrid target risk: `57.99`
- shape-conditioned target risk: `57.69`

This is a real but very small improvement.

`p241_005_mic1`:

- hybrid shift: `25.80`
- shape-conditioned shift: `25.80`
- hybrid target risk: `24.06`
- shape-conditioned target risk: `24.06`

This confirms that the shape gate is selective enough not to damage the
previously rescued high-`f0` feminine row.

`174_50561_000024_000000`:

- unchanged across the tested shape variants

This confirms that the override is not simply a blanket feminine tightening.

## Route Decision

- Keep the hybrid target-bin gate as the active machine baseline.
- Do not promote this first shape-conditioned override to the baseline.

Reason:

- the selectivity is good
- but the benefit is too small to justify another active-stack change

## Immediate Next Step

The next target-side refinement should focus on the remaining structurally
unsafe rows more directly.

Most plausible next candidates:

1. a row-level veto or cap for only `p230_107_mic1` and `2086_149214_000006_000002`
2. a more local bin-selection rule for those rows rather than another global
   or bucket-level threshold
