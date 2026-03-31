# Selective Anchor And p230 Pitch Rescue Fail v1

## Summary

This checkpoint records the next row-aware stabilization pass after the
`anchor075` BigVGAN baseline became the active machine stack.

Two follow-up ideas were tested:

1. selective frame-level source anchoring for only high-delta voiced frames
2. stronger post-vocoder pitch rescue on the worst remaining row

Main conclusion:

- neither follow-up solves the remaining route blocker
- selective frame anchoring slightly improves average structure risk but gives
  back too much targetward movement
- stronger post-vocoder pitch rescue does not save `p230_107_mic1`

So the next route step should move upstream into target-side selective edit
gating, not continue backend-side rescue.

## New Adapter Control

`scripts/run_atrr_vocoder_carrier_adapter.py` now supports:

- `--frame-anchor-l1-threshold`
- `--frame-anchor-min-alpha`

These options start from the pack-level anchor setting and reduce frame-level
edit strength only when the voiced frame edit is unusually large relative to
the source frame distribution.

This was intended to preserve the good rows from `anchor075` while damping only
the most aggressive frames on remaining outliers.

## Selective Anchor Sweep

Baseline stack:

- `frame_distribution_anchor_alpha = 0.75`
- `voiced_target_blend_alpha = 0.75`
- pitch correction trigger `150`
- pitch correction cap `200`

Selective variants:

1. threshold `1.00`, min alpha `0.25`
2. threshold `0.90`, min alpha `0.25`

Outputs:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v4_selective_anchor_sweep/`

## Pack Level Result

Baseline `anchor075`:

- shift: `45.10`
- target log-mel MAE: `0.5693`
- target probe structure risk: `45.76`
- edit-added structure risk: `24.63`

Selective threshold `1.00`:

- shift: `40.02`
- target log-mel MAE: `0.5141`
- target probe structure risk: `44.79`
- edit-added structure risk: `23.66`

Selective threshold `0.90`:

- shift: `40.51`
- target log-mel MAE: `0.5106`
- target probe structure risk: `43.71`
- edit-added structure risk: `22.57`

Reading:

- selective frame damping does reduce structure risk a little
- but the shift loss is too large for the amount of structural gain
- this is not a route-worthy improvement over the plain `anchor075` baseline

## Important Row Level Reading

The selective frame-anchor idea fails on the wrong row.

For `p230_107_mic1`:

- baseline shift: `20.53`
- threshold `1.00` shift: `1.60`
- threshold `0.90` shift: `0.00`

Structure barely improves on that row, while targetward movement collapses.

For `p241_005_mic1`:

- baseline shift: `28.49`
- threshold `1.00` shift: `22.61`
- threshold `0.90` shift: `23.27`

So this stabilization shape is too blunt for the remaining weak rows.

## p230 Single Row Pitch Rescue Test

Because `p230_107_mic1` still showed very large `F0` drift under `anchor075`,
the next narrow question was whether stronger post-vocoder pitch correction
could rescue that row without destroying the edit.

Single-row runs:

1. global pitch correction cap `400`
2. global pitch correction cap `700`
3. voiced-only pitch correction cap `700`

Outputs:

- `artifacts/diagnostics/atrr_carrier_structure_audit/p230_pitch_diag/`

Results:

- cap `400`: shift `4.21`, target risk `64.36`
- cap `700`: shift `0.00`, target risk `64.50`
- voiced-only cap `700`: shift `0.00`, target risk `61.47`

Reading:

- stronger post-vocoder pitch rescue does not recover this row
- the row loses targetward movement before structure improves enough
- `p230_107_mic1` should no longer be treated as a row that backend-side pitch
  rescue is likely to fix

## Route Decision

- Keep `anchor075` as the active machine-only BigVGAN baseline.
- Reject the selective frame-anchor variants as the next main stack.
- Reject stronger backend-side pitch rescue as a likely fix for
  `p230_107_mic1`.

## Immediate Next Step

The next route step should move upstream and become target-side selective edit
gating:

1. keep `anchor075` as the backend baseline
2. stop trying to rescue `p230_107_mic1` with stronger backend-side correction
3. add a target-side confidence or edit-magnitude gate before the carrier input
4. evaluate the next pass with both pack-level and row-level structure audit
