# ATRR Offline Simulator And Scoring Loop v1

## Purpose

This document defines the first implementation-facing simulator for the `ATRR` method family.

The simulator does not reconstruct audio.
It operates only in resonance-distribution space so that the next method loop can be machine-first and cheap.

## Script Entry

- `scripts/simulate_targetward_resonance_residual.py`

## Scope

The simulator should answer one question first:

- if a targetward additive residual is applied in distribution space, do the diagnostic scores move in the right direction at all

This is the lowest-risk check before any reconstruction work.

## Inputs

The first simulator takes:

- a listening-pack style queue csv
- source audio paths from `original_copy`
- source metadata already present in the queue
- target prototypes built from matching opposite-domain source rows

The first default input remains the existing `LSF v7` review queue so the method can be tested against the known failure case.

## Internal Objects

For each row:

1. build source distribution features
2. build a weighted target prototype
3. build a combined soft core mask
4. apply a bounded targetward residual in distribution space
5. score the edited result with the same diagnostic family

## Residual Form

The simulator uses the first practical residual:

- `r_t = a * m_t * d_t + b * (1 - m_t) * d_t`

where:

- `d_t = p_t - x_t`
- `m_t` is the combined core mask
- `a` is the core step size
- `b` is the off-core step size

The first simulator also includes:

- per-bin residual clipping
- cross-frame residual smoothing on voiced frames

## First Control Surface

The initial sweep surface should be:

- `core_step_size`
- `off_core_step_size`
- `frame_smoothness_weight`
- `max_bin_step`

This is intentionally smaller than the full future `ATRR` control set.

The goal of the first pass is not full optimization.
The goal is to test whether the edit object has the right movement behavior in principle.

## Output Metrics

The simulator should write row-level and pack-level summaries for:

- `sim_resonance_distribution_shift_score`
- `sim_core_resonance_coverage_score`
- `sim_over_localized_edit_penalty`
- `sim_context_consistency_score`
- `sim_frame_improvement_mean`

These should remain directly comparable to the existing diagnostic metrics.

## Acceptance Reading

The first useful sign is:

- simulated shift score clearly improves over the observed `v7` processed result
- simulated frame improvement becomes positive on average
- simulated core coverage rises without driving localization penalty to an extreme

The first simulator does not need to prove that the full method works.
It only needs to show that the new edit object points in a better direction than the current `LSF` local-parameter route.

## Boundary

The simulator is not yet:

- an audio method
- a pack builder
- a machine-gate source

It is an implementation bridge between:

- diagnostic evidence
- and future reconstructable method design

## Immediate Next Step

After the simulator runs on `LSF v7`, the next task should be:

- compare simulated `ATRR` scores against the observed `v7` scores
- choose a narrow parameter sweep range
- only then decide whether envelope reconstruction work is justified
