# ATRR Reconstruction Dead End And Strength Escalation Pivot v1

## Summary

This document records the conclusion of the ATRR LSF reconstruction prototype
experiment and the pivot back to direct strength escalation on the LSF main line.

## What Was Attempted

The ATRR reconstruction prototype (`scripts/reconstruct_atrr_lsf_prototype.py`)
was implemented, debugged through six reconstruction runs (v1 through v7 artifacts),
and scored against the machine gate. The goal was to use ATRR mel-distribution
edits to guide a more targeted LSF reconstruction that would move the resonance
distribution more effectively than plain v7 LSF edits.

## What Was Found

### Three bugs were fixed during implementation

See `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md` for the full
bug-fix history. The bugs were real and fixing them was necessary, but fixing
them did not resolve the fundamental design tension described below.

### The ATRR reconstruction faces an irresolvable tension

The ATRR distribution edit and the spectral-centroid-based machine gate measure
different things, and the LSF carrier cannot satisfy both simultaneously:

- To improve the ATRR mel-distribution shift score, the reconstruction must make
  small, targeted per-frame adjustments guided by the mel-space residual.
  These adjustments produce waveform_mean_abs_diff of 0.0002 to 0.010, which is
  insufficient for the machine gate (direction_score near zero).

- To pass the machine gate (direction_score >= 45), the reconstruction must apply
  the full v7 edit strength (scale=1.0), which produces waveform effects equivalent
  to the original v7 LSF run. This means delta_shift_vs_observed = 0.00 and the
  ATRR distribution improvement advantage disappears.

- There is no intermediate operating point where ATRR reconstruction produces both
  a meaningful distribution improvement AND sufficient machine-gate-measurable effect.

### The machine gate already tells us what to do

The v7 machine gate report already contains:

- `strength_escalation_recommendation: escalate_strength_before_next_human`
- `strength_escalation_reason: reviewed_too_weak_dominant`
- `reviewed_too_weak_rows: 8`

This recommendation was present before the ATRR reconstruction experiment began.
The ATRR experiment was an attempt to solve the too_weak problem at the distribution
representation layer rather than by direct strength escalation. That attempt failed
to produce a result that is simultaneously distribution-better and machine-viable.

## Why Direct Strength Escalation Is The Correct Next Step

The v7 human review failure mode is clear:

- The effect is audible but universally too weak.
- The core resonance does not appear to move.
- Artifacts are not the main problem.

This is exactly the failure mode that the post-review strength escalation rule
was designed for. The rule in `docs/01` states:

- if a reviewed pack comes back mostly too_weak
- and artifacts are not the main problem
- then the next step is to raise strength before the next human pass

The correct action is to implement LSF v8 with raised strength parameters,
run it through the machine gate, and if it passes, submit for human review.

## ATRR Experiment Value

The ATRR experiment was not wasted work:

- The distribution diagnostics (docs 71-73) correctly identified that core
  resonance coverage is low and targetward movement is weak in v7.
- The ATRR method design (doc 74) is sound in principle.
- The failure was specifically in the reconstruction bridge: the LSF carrier
  cannot simultaneously satisfy the mel-distribution objective and the
  spectral-centroid-based machine gate.
- If a future route uses a synthesis method with tighter mel-distribution
  control (e.g., vocoder-based), the ATRR distribution edit design could
  be revisited.

## Immediate Next Step

Implement LSF v8:

- raise center_shift_ratios further in the masculine direction
- raise center_shift_ratios further in the feminine direction
- raise pair_width_ratios for masculine if needed
- keep blend at or near 1.0
- run machine sweep to find the strongest setting that does not collapse
  preservation or trigger artifact proxies
- build listening pack and run machine gate
- send to human review only if machine gate passes

The v8 target should aim for avg auto_quant_score >= 80 and direction_score >= 70
while keeping preservation_score >= 95 and no artifact flags.