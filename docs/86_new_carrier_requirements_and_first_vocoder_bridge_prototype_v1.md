# New Carrier Requirements And First Vocoder Bridge Prototype v1

## Summary

This document defines the first concrete follow-up after `LSF` route closure.

The next route should not start from another broad method sweep.
It should start from a narrow carrier prototype with explicit requirements.

The chosen direction is:

- a vocoder-based carrier bridge

The first implementation target is not full audio synthesis yet.
It is a machine-only target export stage that prepares edited target log-mel
objects for a future vocoder carrier.

## Why A Vocoder-Based Carrier Is The Best Next Candidate

The repo already learned three important constraints:

1. `LSF` did not move core resonance in a perceptible way
2. `ATRR` targetward distribution design was not the main failure point
3. the old failure was the constrained carrier and synthesis surface

`docs/80` already recorded the key implication:

- if a future route has tighter mel-distribution control, the `ATRR` design
  could remain valuable

That makes a vocoder-style carrier the most grounded next candidate, because it
can accept a more direct target-envelope or target-distribution object than the
old `LSF` carrier.

## Hard Requirements For The New Carrier

The next carrier must satisfy all of the following:

### 1. Direct core-resonance control

The route must accept a target representation that can move core resonance
structure directly.

It must not reduce the problem to:

- a small set of pole moves
- broad pitch-like movement
- generic high-band lift or darkening

### 2. Stable fixed8 comparison

All future human comparison on the active route must continue to use:

- `experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv`

This keeps route evaluation stable across the carrier pivot.

### 3. Machine-first compatibility

The new route must fit the existing process:

1. build machine candidate
2. score machine diagnostics
3. gate to human review only if justified

### 4. No restart of closed families

Do not reopen:

- `LSF`
- `WORLD full resynthesis`
- old envelope-only routes
- old `WORLD-guided STFT delta` routes

unless there is a materially new synthesis surface, not just a retune.

## Current Repo Constraint

The repo currently has:

- `torch`
- existing distribution diagnostics
- existing `ATRR` simulator
- no integrated neural vocoder implementation or packaged vocoder weights

This means the first prototype should split into two layers:

1. target-object preparation
2. future carrier adapter

The project should not pretend the vocoder carrier already exists in-repo.

## First Prototype Decision

The first concrete prototype is:

- `ATRR vocoder bridge target export`

This stage is machine-only and does not synthesize audio.

Its job is to prepare, for each review row:

- source log-mel
- edited target log-mel
- target prototype distribution
- edited frame distributions
- voiced-frame mask

These objects are the correct boundary between:

- target editing logic
- future vocoder carrier logic

## Implemented Prototype Asset

The first bridge-target export script now exists:

- `scripts/export_atrr_vocoder_bridge_targets.py`

It reuses:

- `scripts/extract_resonance_distribution_diagnostics.py`
- `scripts/simulate_targetward_resonance_residual.py`

and exports:

- per-row `.npz` target packages
- machine summary CSV
- summary markdown

Current fixed8 export outputs:

- `artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/`

## What The Export Produces

For each row, the exported `.npz` contains:

- `source_log_mel`
- `target_log_mel`
- `source_distribution`
- `target_distribution`
- `target_occupancy`
- `edited_frame_distributions`
- `voiced_mask`

This is enough for the next carrier stage to consume without rebuilding the
full target-edit logic.

## First Export Result

The initial fixed8 export ran successfully on all 8 rows.

Summary:

- rows: `8`
- avg simulated shift score: `58.42`
- avg simulated core coverage: `69.42`

This is not a proof of audible success.

It is only proof that the target-side bridge objects can now be generated in a
stable, reusable form for a new carrier.

## Next Prototype Stage

The next actual implementation target should be:

- a narrow vocoder carrier adapter that consumes the exported `.npz` targets

The adapter should be deliberately minimal:

- machine-only first
- fixed8 only
- one carrier integration path
- no broad sweep yet

## Preferred Adapter Boundary

The first adapter should expose a simple contract:

input:

- one target `.npz`

output:

- one reconstructed waveform
- one lightweight synthesis summary row

The adapter must report:

- synthesis success or failure
- output path
- waveform duration match
- loudness drift
- clipping ratio
- `F0` preservation drift

That is enough to plug it into the existing machine queue logic.

## Immediate Next Step

The next implementation task should be:

1. define the vocoder carrier adapter interface
2. check what external or local vocoder asset can be used without changing repo
   boundaries
3. build one machine-only adapter prototype against the exported fixed8 targets
