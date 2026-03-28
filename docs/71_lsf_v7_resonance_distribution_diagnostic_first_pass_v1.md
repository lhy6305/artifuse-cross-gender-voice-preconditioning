# LSF v7 Resonance Distribution Diagnostic First Pass v1

## Scope

This document records the first implementation and first result of the resonance-distribution diagnostic plan.

Implementation:

- `scripts/extract_resonance_distribution_diagnostics.py`

Outputs:

- `artifacts/diagnostics/lsf_v7_resonance_distribution_v1/resonance_distribution_diagnostic_summary.csv`
- `artifacts/diagnostics/lsf_v7_resonance_distribution_v1/RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md`

## What Was Measured

The first-pass diagnostic added four metrics:

- `resonance_distribution_shift_score`
- `core_resonance_coverage_score`
- `over_localized_edit_penalty`
- `context_consistency_score`

The target prototype was built from same-dataset natural originals of the target gender already present in the `v7` review pack.

## Pack-Level Result

For `LSF v7`, the first-pass averages are:

- `avg resonance_distribution_shift_score = 41.70`
- `avg core_resonance_coverage_score = 46.40`
- `avg over_localized_edit_penalty = 26.20`
- `avg context_consistency_score = 46.44`

By direction:

- `feminine`
  - `avg shift score = 35.72`
  - `avg core coverage = 52.68`
  - `avg localization penalty = 26.78`
  - `avg context consistency = 44.35`
- `masculine`
  - `avg shift score = 47.67`
  - `avg core coverage = 40.12`
  - `avg localization penalty = 25.62`
  - `avg context consistency = 48.54`

## Reading Of The Result

This first pass supports part of the current hypothesis, but not all of it.

What it supports:

- movement toward the target prototype is weak or inconsistent
- core-resonance coverage is limited, especially on the masculine side

What it does not strongly support:

- the edit being extremely narrow or trivially localized

The localization penalty is not especially high. That suggests the current failure mode is not just:

- edit only one tiny band

It looks more like:

- the edit is broad enough to be audible
- but the movement is not consistently targetward
- and too little of the edit mass lands on the core resonance structure

## Practical Meaning

This is useful because it sharpens the route constraint.

The next method should not simply:

- increase strength again
- or only widen the edited frequency region

The next method should instead aim to:

- increase targetward movement of the full-band resonance distribution
- increase edit mass inside core resonance support
- improve frame-level consistency of the movement

## Immediate Next Step

Before any new experiment pack is built, the diagnostic side should be refined once more.

The next refinement target is:

- better target prototypes
- stronger context conditioning
- a more explicit definition of core resonance support
