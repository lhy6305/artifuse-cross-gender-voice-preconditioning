# Strength Conditioned Bin Gate Rejected v1

## Summary

This checkpoint records the first attempt to improve the new hybrid target-side
bin gate through utterance-level edit-strength conditioning.

The idea was:

- keep the new direction-conditioned bin-gate baseline
- detect weak target packages through utterance-level source-target `EMD`
- use different direction thresholds only on those weak packages

This did not improve the route.

The result is a rejection of this specific strength-conditioned extension, not
of the hybrid target-bin gate baseline itself.

## Why This Variant Was Tested

After the hybrid target-bin gate became the active machine baseline, the two
main remaining high-risk rows were:

- `p230_107_mic1`
- `2086_149214_000006_000002`

The immediate hypothesis was that those rows might need weaker or stronger
target-side suppression depending on their utterance-level target-package
strength.

So the next narrow test conditioned the delta threshold on source-target `EMD`.

## New Control

`scripts/run_atrr_vocoder_carrier_adapter.py` now supports:

- `--target-bin-source-emd-cutoff`
- `--target-bin-delta-threshold-masculine-weak`
- `--target-bin-delta-threshold-feminine-weak`

These only apply when the package-level source-target `EMD` falls below the
configured cutoff.

## Tested Variant

Baseline hybrid:

- masculine delta `0.010`
- feminine delta `0.015`
- occupancy `0.05`

Strength-conditioned variant:

- source-target `EMD` cutoff `0.035`
- weak masculine delta `0.015`
- weak feminine delta `0.005`

Output:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v8_strength_conditioned_bin_gate/`

## Pack Level Result

Hybrid baseline:

- shift: `41.65`
- target probe structure risk: `36.40`
- edit-added structure risk: `15.26`

Strength-conditioned variant:

- shift: `38.74`
- target probe structure risk: `36.55`
- edit-added structure risk: `15.42`

Reading:

- the new conditioning slightly regresses the pack average
- it does not buy meaningful structural improvement
- it therefore does not justify replacing the current hybrid baseline

## Important Row Level Reading

`2086_149214_000006_000002`:

- hybrid shift: `37.87`
- conditioned shift: `38.62`
- hybrid target risk: `57.99`
- conditioned target risk: `59.36`

This row does not improve in the direction that matters.

`p230_107_mic1`:

- hybrid shift: `36.37`
- conditioned shift: `28.10`
- hybrid target risk: `65.75`
- conditioned target risk: `63.72`

This row gets only a small risk reduction while losing too much movement.

`p241_005_mic1`:

- hybrid shift: `25.80`
- conditioned shift: `24.62`
- hybrid target risk: `24.06`
- conditioned target risk: `25.21`

This row also regresses slightly.

## Route Decision

- Keep the direction-conditioned hybrid target-bin gate as the active machine
  baseline.
- Reject this first utterance-level strength-conditioned extension.

## Immediate Next Step

The next target-side refinement should not be another simple weak-package
override by source-target `EMD`.

More plausible next candidates are:

1. a finer condition keyed to `f0` bucket
2. a condition keyed to target-package shape rather than only scalar `EMD`
3. a row-level veto or cap on only the remaining structurally unsafe rows
