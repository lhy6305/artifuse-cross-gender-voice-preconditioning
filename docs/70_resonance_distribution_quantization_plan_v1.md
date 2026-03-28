# Resonance Distribution Quantization Plan v1

## Goal

The next step is to stop treating resonance as a small edit to a few local bands and to start modeling it as a structured full-band distribution.

This plan defines how to make that idea operational and measurable.

## Problem Statement

The recent `LSF` results show a consistent pattern:

- the pack can become audible
- the pack can remain artifact-safe
- the core resonance can still fail to move in a convincing way

This suggests that local edits to a few pair parameters or a few coarse bands are not enough.

## Working Hypothesis

Gender-related resonance is better approximated as a structured distribution over the full spectral envelope, rather than a small set of isolated band moves.

The distribution should be described across:

- frequency
- time
- voiced harmonic support
- phonetic or vowel context

## Engineering Question

Can this distribution be separated and quantified in a way that is usable for model selection and later editing work?

The answer is yes, at the level of acoustic proxies.

The goal is not to recover the true physical cavity state. The goal is to build stable, useful acoustic signatures that track the resonance structure better than the current local-band metrics.

## Proposed Representation

### 1. Full-band envelope distribution

For each voiced frame:

- compute a smoothed spectral envelope over the full usable band
- represent it on a dense perceptual frequency axis, such as `ERB` or `mel`
- normalize to remove overall gain so that the representation focuses on distribution shape

This produces a frame-level resonance distribution vector.

### 2. Time support

A single frame is not enough.

For each utterance or segment, summarize:

- frame mean
- frame variance
- voiced-only temporal occupancy
- short-range temporal stability

This distinguishes a stable resonance pattern from a brief local perturbation.

### 3. Context-conditioned prototypes

Build reference prototypes conditioned on:

- source or target domain
- coarse vowel or phone class when available
- F0 bin
- dataset group if needed

This avoids comparing all frames to a single global average that mixes incompatible articulation states.

## Core Metrics

### 1. Resonance Distribution Shift Score

Measure whether the processed distribution moves toward the target prototype.

Candidate distance functions:

- `Wasserstein distance`
- `Earth mover style distance`
- `cosine distance` as a cheap baseline

Operational form:

- compare `original -> processed`
- compare `original -> target prototype`
- compare `processed -> target prototype`
- reward movement that reduces distance to the target prototype

### 2. Core Resonance Coverage Score

Measure whether the change affects the main resonance structure instead of only a peripheral region.

A simple first version:

- mark bins with high envelope energy or persistent occupancy
- measure how much of the edit falls inside this core support
- penalize edits that sit mostly outside the core support

This is the direct counter to the failure mode:

- audible change
- but no convincing movement of core resonance

### 3. Over-Localized Edit Penalty

Penalize edits that are too concentrated in a small frequency region.

A simple first version:

- compute the edit distribution across the full-band envelope
- estimate concentration with entropy or coverage width
- penalize extremely narrow edits

This is the direct counter to:

- moving only one narrow region
- leaving the rest of the resonance distribution unchanged

### 4. Context Consistency Score

Measure whether the direction of movement is stable across:

- voiced frames
- F0 bins
- coarse vowel or phone buckets

This helps separate a real structural shift from a sparse accidental effect.

## Minimal Viable Implementation

The first implementation does not need articulatory labels or a new model.

### Stage A

Add a diagnostic extractor that computes, for each file pair:

- full-band envelope vectors on a perceptual axis
- voiced-only frame summaries
- original, processed, and delta distributions

### Stage B

Add utterance-level summary metrics:

- `resonance_distribution_shift_score`
- `core_resonance_coverage_score`
- `over_localized_edit_penalty`
- `context_consistency_score`

### Stage C

Add these metrics to the review queue and machine report as diagnostic-only columns first.

Do not gate on them immediately.

First check whether they explain the known subjective pattern:

- audible but still too weak
- no artifact
- core resonance still not moving

## Reuse Of Existing Infrastructure

The current queue builder already computes several coarse full-pack diagnostics, including:

- centroid shift
- log-centroid-minus-log-F0 shift
- low-mid share shift
- presence share shift
- brilliance share shift

These are useful but too coarse.

The new distributional metrics should sit next to them, not replace them immediately.

## Expected Payoff

If the hypothesis is correct, this plan should improve two things:

1. model selection:
   - reject candidates that only create peripheral audible changes
2. target definition:
   - define resonance change as full-distribution movement rather than narrow band movement

## Immediate Next Step

Before creating another experiment pack, implement the diagnostic side first.

The first concrete deliverable should be:

- a script that extracts resonance-distribution diagnostics for original and processed pairs
- a compact report on whether those diagnostics explain the current `LSF v7` failure mode
