# LSF v7 Resonance Distribution Diagnostic Refined v2

## Scope

This document records the refined `v2` pass of the resonance-distribution diagnostics for `LSF v7`.

Implementation:

- `scripts/extract_resonance_distribution_diagnostics.py`

Outputs:

- `artifacts/diagnostics/lsf_v7_resonance_distribution_v2/resonance_distribution_diagnostic_summary.csv`
- `artifacts/diagnostics/lsf_v7_resonance_distribution_v2/RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md`

## What Changed From v1

The `v2` diagnostic improved two things:

1. target prototype construction
   - weighted by F0 proximity
   - weighted by source-target distribution similarity
2. core support definition
   - no longer only energy-ranked mean support
   - now also uses persistent occupancy support across voiced active frames

## Pack-Level Result

For `LSF v7`, the refined `v2` averages are:

- `avg resonance_distribution_shift_score = 38.39`
- `avg core_resonance_coverage_score = 46.28`
- `avg over_localized_edit_penalty = 26.20`
- `avg context_consistency_score = 44.74`
- `avg frame_improvement_mean = -0.004726`

By direction:

- `feminine`
  - `avg shift score = 30.21`
  - `avg core coverage = 51.26`
  - `avg localization penalty = 26.78`
  - `avg context consistency = 41.27`
  - `avg frame improvement mean = -0.008413`
- `masculine`
  - `avg shift score = 46.58`
  - `avg core coverage = 41.30`
  - `avg localization penalty = 25.62`
  - `avg context consistency = 48.21`
  - `avg frame improvement mean = -0.001038`

## Reading Of The Result

The refined pass makes the earlier conclusion stronger, not weaker.

What now looks unlikely:

- that the main problem is only a too-narrow local edit

What now looks more likely:

- movement toward the target resonance distribution is weak
- frame-level movement is inconsistent
- average frame improvement is slightly negative at the pack level
- core-resonance coverage stays limited, especially on the masculine side

This means the current route is not mainly missing because it edits too little bandwidth.

It is missing because:

- the edit does not move the resonance distribution reliably toward the target
- and too little of the edit mass lands on the structural resonance core

## Practical Constraint For The Next Method

The next method should not be designed as:

- another generic strength increase
- another wider-band version of the same local edit

The next method should be designed around:

- explicit targetward distribution movement
- explicit control of core-support hit rate
- stronger context conditioning for the target definition

## Immediate Next Step

The diagnostic phase is now strong enough to constrain the next design step.

The next work item should be:

- define a new edit object or target representation that can directly optimize targetward resonance-distribution movement, instead of only changing a few local parameters
