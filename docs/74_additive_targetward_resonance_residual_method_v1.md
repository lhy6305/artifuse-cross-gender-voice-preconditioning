# Additive Targetward Resonance Residual Method v1

## Purpose

This document turns the edit-object plan into a concrete first method family.

The goal is to define a method that can:

- move the resonance distribution toward the target domain
- place more edit mass on the structural resonance core
- remain stable across voiced frames
- avoid reducing the problem to a small number of local band edits

## Method Name

The first concrete method family is:

- `ATRR`

Expanded:

- `additive targetward resonance residual`

## Why This Method

The refined diagnostics now suggest that the current failure mode is:

- audible change exists
- targetward resonance movement is weak
- frame-level movement is inconsistent
- core-resonance coverage is too low
- over-localization is not the main dominant error

This means the next method should directly edit the resonance-distribution representation instead of only moving a few interpretable local parameters.

## Core Representation

### Frame Representation

For each voiced active frame, define:

- `x_t`
  - source frame resonance distribution
  - represented as a gain-normalized smoothed log-envelope on a dense perceptual axis
- `p_t`
  - context-conditioned target prototype
- `d_t = p_t - x_t`
  - targetward residual direction

Recommended first representation:

- log-envelope on a `mel` or `ERB` axis
- approximately `64` to `96` bins
- full usable speech band
- gain-normalized per frame so the edit targets shape rather than loudness

### Core Support Mask

For each frame, define a soft core mask `m_t` over the same frequency bins.

The first version should combine:

- source occupancy support
- source high-energy support
- target prototype support

This mask should be soft-valued, not binary.

## Target Prototype Construction

The target prototype should not be one global average.

The first `ATRR` implementation should build `p_t` from a weighted mixture of target-domain reference frames using:

- direction
- dataset group
- voiced active state
- `F0` proximity
- source-target envelope similarity

Recommended prototype modes:

- `utterance_conditioned`
- `segment_conditioned`
- `frame_neighborhood_conditioned`

The first implementation should start with `segment_conditioned` or a light `frame_neighborhood_conditioned` mode rather than a fully global prototype.

## Residual Construction

The method edits the frame representation by constructing an additive residual:

- `r_t`

The first practical form should be:

- `r_t = a * m_t * d_t + b * (1 - m_t) * d_t`

with:

- `a > b >= 0`
- `a` controlling the step size inside the structural resonance core
- `b` allowing bounded off-core support movement without turning the edit into a narrow spike

The edited frame representation becomes:

- `y_t = x_t + r_t`

## Required Constraints

### 1. Targetward Improvement Constraint

For each frame, the edit should improve distance to the target prototype:

- `dist(y_t, p_t) < dist(x_t, p_t)`

This should be enforced softly first, then hardened if needed.

### 2. Core Support Priority

The method should reward edit mass inside `m_t` and penalize edit mass that escapes too far outside the structural support.

This is the main counter to:

- audible change without core resonance movement

### 3. Off-Core Penalty

The method should include a penalty for wide residual mass that does not contribute to targetward improvement.

This is different from the old narrow-band problem.

The new risk is:

- broad but low-value movement
- broad but wrong-direction movement

### 4. Frame Smoothness

The residual should change smoothly across neighboring voiced frames.

The first version should regularize:

- `r_t - r_{t-1}`

This is needed because the diagnostics showed weak frame consistency.

### 5. High-Band Preservation Without Hard Bypass

The method should not encode `masculine` as generic darkening.

Instead:

- high-band changes must still be target-directed
- high-band movement may be small
- high-band movement must not default to systematic suppression

This avoids repeating the earlier bottle-tone and muffled failure mode.

## Reconstruction Boundary

`ATRR` should edit the resonance envelope object, not the excitation or the residual path.

The reconstruction boundary for the first implementation should therefore be:

- preserve original phase
- preserve original excitation timing as much as possible
- apply the edit through the envelope path

The first reconstruction strategy should be conservative:

1. build an edited full-band envelope target from `y_t`
2. fit a stable parametric envelope representation to that target
3. resynthesize with original phase-residual structure preserved as much as possible

Candidate stable carriers for the fitted envelope:

- cepstral envelope
- stable `LSF` envelope
- direct smoothed spectral-envelope gain curve if inversion remains stable

The key point is that the carrier is secondary.
The primary edit object is the targetward envelope residual in distribution space.

## First Parameter Set

The first sweepable control set should be:

- `core_step_size`
- `off_core_step_size`
- `frame_smoothness_weight`
- `prototype_mode`
- `prototype_f0_weight`
- `prototype_similarity_weight`
- `core_mask_source_weight`
- `core_mask_target_weight`
- `off_core_penalty`
- `max_bin_step_db`

This is a better search surface than only:

- `center_shift_ratios`
- `pair_width_ratios`
- `blend`

## Machine-Side Acceptance Signals

Before any new human review, `ATRR` candidates should show improvement on:

- `resonance_distribution_shift_score`
- `core_resonance_coverage_score`
- `context_consistency_score`
- `frame_improvement_mean`

and should avoid regression on:

- artifact proxies
- presence and brilliance collapse
- `F0` or voiced-structure preservation

## Minimal Implementation Path

### Stage 1

Implement an offline `ATRR` diagnostic simulator that:

- constructs `x_t`
- builds `p_t`
- applies bounded residuals in distribution space
- evaluates the result with the existing diagnostics

No audio reconstruction is needed at this stage.

### Stage 2

Add a conservative envelope reconstruction path from edited distribution space back to a synthesis-safe carrier representation.

### Stage 3

Run a machine-only sweep over the first `ATRR` control set.

Only candidates that clearly improve the new diagnostic scores and pass the existing machine gate should reach a listening pack.

## Immediate Next Step

The next implementation-facing task should be:

- define the offline `ATRR` simulator interface and scoring loop before attempting audio reconstruction
