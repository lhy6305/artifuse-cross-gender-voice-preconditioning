# Representation Layer Route: LSF Probe v6

## Purpose

`LSF v6` was the first formal LSF candidate that moved the masculine route away from broad dark tilt and toward lower-formant geometry with preserved air.

## Core Change

The masculine route switched from:

- `brightness_down`

to:

- `formant_lowering_preserve_air`

The implementation also added:

- `pair_width_ratios`

This concentrated the main action on lower-formant geometry and pair spacing instead of blanket high-band suppression.

## Machine Result

The best `v6` machine-only variant was `lower_geom_v6b`.

Pack-level machine metrics:

- `avg_auto_quant_score = 81.13`
- `avg_auto_direction_score = 70.97`
- `avg_auto_effect_score = 87.46`
- `fail_rows = 0`

## Human Result

Formal human review for `v6` was completed before this task.

The key conclusion was:

- the route was not rejected
- the pack was not dominated by artifacts
- the whole pack was still too weak

Operational summary:

- `effect_audible = yes 2 / maybe 6 / no 0`
- `strength_fit = too_weak 8 / 8`

## Decision

`v6` is kept as a valid route checkpoint, but not as a viable final-strength pack.

The next action implied by `v6` was:

- do not repeat another same-strength human pack
- raise pack strength first
- then send the stronger candidate to human review

That stronger follow-up is documented in:

- `docs/63_representation_layer_lsf_probe_v7.md`
