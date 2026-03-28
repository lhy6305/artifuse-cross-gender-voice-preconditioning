# Targetward Resonance Distribution Edit Object v1

## Purpose

The diagnostics are now strong enough to constrain the next method design.

The next method should not be another local-parameter edit with a larger strength knob.
It should be an edit object that directly targets movement of the resonance distribution toward the target domain.

## Why A New Edit Object Is Needed

The current `LSF` route edits a small set of interpretable parameters:

- `center_shift_ratios`
- `pair_width_ratios`
- `blend`

This was useful for initial probing, but the refined diagnostics now show:

- weak targetward movement
- weak frame-level consistency
- low core-resonance coverage
- no strong evidence that over-localization is the main failure mode

That means the current parameterization is too indirect.

## Proposed Edit Object

The next edit object should operate on:

- a full-band resonance-distribution residual
- with explicit targetward movement constraints
- and explicit core-support weighting

Instead of saying:

- move `F2`
- widen one pair
- blend more

the method should say:

- move the current resonance distribution toward a target prototype
- put more edit mass on the structural resonance core
- keep the movement stable across voiced frames

## Minimal Mathematical Form

Let:

- `x_t` be the current frame-level resonance distribution
- `p_t` be a context-conditioned target prototype
- `m_t` be a core-support weighting mask

The new edit object should produce an edit residual `r_t` such that:

- `x_t + r_t` moves closer to `p_t`
- edit mass inside `m_t` is rewarded
- edit mass outside `m_t` is downweighted
- frame-to-frame residual changes are regularized

This makes the optimization target explicit.

## Design Options

### Option A. Additive envelope-distribution residual

Operate directly on a smoothed full-band envelope representation.

Advantages:

- closest match to the new diagnostics
- easiest to score with the current metrics

Costs:

- requires a new inversion or reconstruction path

### Option B. Basis-weighted residual over learned resonance atoms

Represent the envelope distribution with a small basis and edit the basis weights.

Advantages:

- lower-dimensional control
- easier to regularize

Costs:

- requires building a resonance basis first

### Option C. Prototype-directed transport in resonance space

Estimate a conservative transport field from source distribution to target prototype and apply only a bounded step.

Advantages:

- naturally expresses targetward movement
- may fit the current prototype diagnostics well

Costs:

- more care needed for stability and invertibility

## Recommended First Implementation

Start with Option A.

Reason:

- the current diagnostics already operate in an envelope-distribution space
- this gives the shortest path from diagnosis to a new edit method
- it avoids premature commitment to a basis-learning step

## Required Constraints

Any new edit object should be scored or regularized against:

- targetward distribution improvement
- core-resonance coverage
- context consistency
- preservation of F0 and voiced structure

This means the diagnostic metrics should become part of the design loop, not only a post-hoc report.

## Expected Interface

The next method family should expose controls closer to:

- `target_step_size`
- `core_support_weight`
- `off_core_penalty`
- `frame_smoothness_weight`
- `context_conditioning_mode`

and less around:

- local pair shift only
- single-band strength only

## Immediate Next Step

Before building a new listening pack, define one concrete method family around this edit object.

The next concrete design document should therefore specify:

- which representation will carry the full-band residual
- how the target prototype is chosen per frame or segment
- how the residual is constrained before reconstruction
