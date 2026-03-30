# Post LSF v8 Review And Conditioned Priors Pivot v1

## Review Result

Formal human review for `LSF v8` is now complete.

Queue file:

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/listening_review_queue.csv`

Machine review summary after the queue was filled:

- `reviewed_outcome = reviewed_non_null`
- `reviewed_too_weak_rows = 3`
- `strength_escalation_recommendation = no_strength_escalation_flag`

Listening review rollup:

- `rows = 8`
- `effect_audible = yes 6 / maybe 2 / no 0`
- `direction_correct = yes 2 / maybe 4 / n_a 2`
- `artifact_issue = slight 5 / no 2 / n_a 1`
- `strength_fit = ok 3 / too_weak 3 / n_a 2`
- `proposed_disposition = watch_with_risk`

## User Qualitative Diagnosis

The user reported a clearer failure pattern than the sparse queue fields alone:

- the core resonance still does not appear to move
- female to male still produces a muffled bottle like color
- female to male strength distribution is uneven across `f0`
- male to female now tends to overproduce upper band texture, described as
  plastic paper like high frequency noise

These notes are the key handoff signal from this review.

## Interpretation

`v8` is not another pure `too_weak` result.

The pack is audible, but the audible change is landing in the wrong place:

- male direction is still not changing core resonance correctly and is paying
  for its effect with muffled bottle coloration
- female direction is achieving audibility partly through excess upper band
  excitation instead of a cleaner core resonance shift

This means the project should not treat `v9` as a direct strength escalation.
The post review auto rule does not recommend that, and the subjective failure
mode has changed from weak only to wrong distribution plus artifact risk.

## Route Decision

Stay on the `LSF` route for one more iteration, but change the operating
principle.

The next iteration should add stronger priors and split the two directions
explicitly instead of using a mostly symmetric strength bump:

- for female to male, prioritize anti muffle and anti bottle constraints
- for male to female, prioritize anti plastic and anti over brilliance
  constraints
- for both directions, add `f0` conditioned strength control so the effect is
  not concentrated in only part of the pitch range

This is not yet a full synthesis family pivot.
It is a conditioned `LSF v9` pivot.
If conditioned `LSF v9` still fails to move core resonance without these
artifacts, the next step should be a synthesis family change rather than
another `LSF` strength retune.

## Required Priors For v9

### 1. Direction specific priors

Do not use one generic stronger edit family for both directions.

- female to male should reduce broad low mid loading and avoid width growth
  patterns that darken the tract into a bottle color
- male to female should stop relying on broad upper band lift as the main cue

### 2. F0 conditioned control

The v8 review surfaced obvious unevenness across `f0`.
The next iteration should bucket or normalize strength by `f0` so low, mid,
and high pitch regions do not receive the same raw edit scale.

### 3. Core over edge priority

The next objective should explicitly favor moving the low and mid resonance
structure before adding more edge brightness or brilliance motion.

## Immediate Next Step

Build a conditioned `LSF v9` diagnostic plan:

1. summarize `v8` review by direction and `f0` band
2. define separate female to male and male to female prior constrained edits
3. sweep only inside that constrained `v9` family
4. send to human review only if the machine gate stays green and the new
   diagnostics show better core targeting without the current artifact pattern
