# f0 Conditioned Bin Gate Probe v1

## Summary

This checkpoint records the first `f0` conditioned refinement pass on top of the
active hybrid target-side bin gate.

The goal was narrow and explicit:

- keep the current hybrid direction-conditioned gate
- test only the two remaining problem buckets
- avoid reopening a broad parameter sweep

The two tested buckets were:

- `masculine mid_f0`
- `feminine high_f0`

Result:

- `masculine mid_f0` tightening gives a small pack-level structure gain, but it
  also weakens `p230_107_mic1`
- `feminine high_f0` tightening hurts `p241_005_mic1`

So the current hybrid target-bin gate remains the active machine baseline.

## Tested Variants

Baseline hybrid:

- masculine delta `0.010`
- feminine delta `0.015`
- occupancy `0.05`

Narrow variants:

1. `masculine mid_f0 = 0.015`
2. `feminine high_f0 = 0.020`
3. both changes together

Outputs:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v9_f0_conditioned_bin_gate_sweep/`

## Pack Level Result

Baseline hybrid:

- shift: `41.65`
- target probe structure risk: `36.40`
- edit-added structure risk: `15.26`

`masculine mid_f0 = 0.015`:

- shift: `40.59`
- target probe structure risk: `35.73`
- edit-added structure risk: `14.60`

`feminine high_f0 = 0.020`:

- shift: `39.92`
- target probe structure risk: `36.31`
- edit-added structure risk: `15.18`

Combined:

- shift: `38.85`
- target probe structure risk: `35.65`
- edit-added structure risk: `14.52`

Reading:

- the pack-level gains are real but small
- the tradeoff becomes unacceptable once the remaining weak rows are checked

## Important Row Level Reading

`p230_107_mic1` under `masculine mid_f0 = 0.015`:

- shift: `36.37 -> 28.10`
- target risk: `65.75 -> 63.72`

This is only a small structure gain for too much movement loss.

`p241_005_mic1` under `feminine high_f0 = 0.020`:

- shift: `25.80 -> 12.95`
- target risk: `24.06 -> 24.60`

This is clearly the wrong tradeoff.

`2086_149214_000006_000002` under `feminine high_f0 = 0.020`:

- shift: `37.87 -> 38.16`
- target risk: `57.99 -> 57.69`

This is too small to justify the damage to `p241`.

## Route Decision

- Keep the direction-conditioned hybrid target-bin gate as the active machine
  baseline.
- Do not promote any of the tested `f0` conditioned variants to the new
  baseline.

## Immediate Next Step

The next refinement should stay target-side but become more selective than a
whole-bucket threshold change.

Most plausible next candidates:

1. a target-shape-conditioned gate for the remaining bad rows
2. a row-level veto or cap for only the structurally unsafe rows
3. a more local bin-selection rule inside the existing hybrid gate
