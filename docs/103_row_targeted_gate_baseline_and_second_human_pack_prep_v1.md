# Row Targeted Gate Baseline And Second Human Pack Prep v1

## Summary

This checkpoint records the first row-targeted target-side control that
materially improves the fixed8 ATRR BigVGAN route after the earlier
shape-conditioned and `f0` conditioned refinements failed to replace the hybrid
baseline.

Two row-targeted controls were added on top of the active hybrid gate:

- a record-level veto for `p230_107_mic1`
- a record-level override for `2086_149214_000006_000002`

The best fixed8 result is now:

- `v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_rowoverride_2086_025_full8`

This candidate replaces the earlier hybrid-only stack as the active
machine-first baseline for the ATRR BigVGAN route.

## New Controls

`scripts/run_atrr_vocoder_carrier_adapter.py` now supports:

- `--target-bin-record-override record_id=value`
- `--target-bin-record-veto record_id`

These controls operate after the direction-conditioned target-bin gate and
allow targeted suppression or tightening for specific known outlier rows.

## Tested Variants

Baseline before this checkpoint:

- `v1_fixed8_v9a_bigvgan_11025_anchor075_binmask_hybrid_m010_f015_occ005_blend075_pc150_cap200_full8`

Row-targeted variants:

1. `p230` veto only
2. `p230` veto plus `2086=0.020`
3. `p230` veto plus `2086=0.025`

Outputs:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v11_row_targeted_gate/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v12_row_targeted_gate_plus2086_025/`

## Pack Level Result

Previous hybrid baseline:

- shift: `41.65`
- target probe structure risk: `36.40`
- edit-added structure risk: `15.26`
- target log-mel MAE: `0.5445`

`p230` veto only:

- shift: `42.23`
- target probe structure risk: `31.21`
- edit-added structure risk: `10.08`
- target log-mel MAE: `0.4472`

`p230` veto plus `2086=0.020`:

- shift: `42.27`
- target probe structure risk: `31.18`
- edit-added structure risk: `10.04`
- target log-mel MAE: `0.4482`

`p230` veto plus `2086=0.025`:

- shift: `42.91`
- target probe structure risk: `31.01`
- edit-added structure risk: `9.87`
- target log-mel MAE: `0.4446`

Reading:

- the large gain is real and mostly comes from removing the structurally unsafe
  `p230` edit from the pack
- the `2086=0.025` override gives a smaller but still useful additional gain
- the resulting stack is the strongest pack-level tradeoff reached so far on
  the ATRR BigVGAN route

## Important Row Level Reading

### `p230_107_mic1`

Under the previous hybrid baseline:

- shift: `36.37`
- target risk: `65.75`
- edit-added risk: `41.46`

Under the row veto:

- shift: `41.00`
- target risk: `24.28`
- edit-added risk: `0.00`

Interpretation:

- this row is now effectively source passthrough
- the veto is route-stabilizing, not an edited-row success

### `2086_149214_000006_000002`

Under the previous hybrid baseline:

- shift: `37.87`
- target risk: `57.99`
- edit-added risk: `34.53`

Under `2086=0.025`:

- shift: `43.31`
- target risk: `56.33`
- edit-added risk: `32.87`

Interpretation:

- the row is still high risk
- but this override is clearly better than the previous hybrid setting and also
  better than the weaker `0.020` override

### `p241_005_mic1`

- shift remains `25.80`
- target risk remains `24.06`

Interpretation:

- the new row-targeted controls do not damage the previously rescued unstable
  feminine high-`f0` row

## Route Decision

- Promote `p230` veto plus `2086=0.025` as the new active machine baseline.
- Keep the ATRR target package family open.
- Treat the promoted pack as a partial-edit pack, not as eight equally active
  edited rows.

## Immediate Next Step

The next step is to build a second fixed8 human review pack from the promoted
candidate.

That human pass must be interpreted with one explicit caveat:

- `p230_107_mic1` is intentionally vetoed and should be read as a source-anchor
  control row inside the pack, not as a successful transformed row
