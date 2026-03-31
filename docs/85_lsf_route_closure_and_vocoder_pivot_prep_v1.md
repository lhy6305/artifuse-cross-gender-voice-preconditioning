# LSF Route Closure And Vocoder Pivot Prep v1

## Summary

The `LSF` main line is now closed as an active synthesis route.

Reason:

- `v7` was audible but universally too weak
- `v8` became more audible, but still did not move core resonance correctly
- conditioned `v9` on the restored fixed 8-sample comparison set is still
  effectively imperceptible

This means the project should not continue to `LSF v10`.

## Final LSF Human Result

Authoritative comparison pack:

- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/`

Supporting review rollup:

- `artifacts/listening_review_rollup/lsf_v9_fixed8_v9a/`

Supporting machine report:

- `artifacts/machine_gate/lsf_v9_fixed8_v9a/`

Sparse fixed8 review facts:

- reviewed: `8 / 8`
- audible: `yes = 0`, `maybe = 2`, `no = 6`
- strength too weak: `4`

The user then provided the pack-level authoritative conclusion:

- the pack remains effectively indistinguishable
- no further relisten is needed

That conclusion is stronger than the sparse row encoding and should be treated
as the final route-level decision.

## Why LSF Is Closed

Across the full `LSF` sequence, the route never reached the required behavior:

- stable perceptibility on the fixed human comparison set
- clear movement of core resonance rather than broad pitch-like impression
- acceptable directional effect without relying on the wrong edge cues

The route was given three distinct chances:

1. direct strength escalation
2. direction-conditioned priors
3. `f0` conditioned control on a stable comparison pack

The route still failed to produce a usable human result.

Further `LSF` tuning is now low-value iteration.

## What Survives From The Work

The following assets remain useful:

- the fixed 8-sample human comparison manifest
- the machine-first workflow and gate
- the `ATRR` targetward distribution design
- the post-review conclusion that the missing capability is direct control of
  core resonance, not just stronger edge movement

The main failure was the carrier and synthesis surface, not the need for better
diagnostics.

## Next Route Hypothesis

The next route should use a new synthesis family with tighter target-envelope
or target-distribution control than the `LSF` carrier.

The most grounded next candidate is a vocoder-based carrier family.

Why this candidate:

- `docs/80` already recorded that the `ATRR` design could remain valid if a
  future route had tighter mel-distribution control
- `LSF` failed specifically as the constrained carrier
- the next route must be able to express target resonance structure directly,
  not only through coarse pole or pair edits

This does not mean returning to old `WORLD full resynthesis`.
That route was already rejected for artifact reasons.

The new route must be a new carrier family, not a restart of previously closed
implementations.

## Immediate Research Plan

### Phase 1. Define the new carrier requirements

Write a short design checkpoint that freezes the requirements for the next
synthesis family:

- must target core resonance directly
- must not collapse into broad pitch-like change
- must preserve the existing fixed8 human comparison set
- must still support the machine-first workflow

### Phase 2. Build a narrow candidate shortlist

Shortlist only carrier families that are genuinely different from `LSF`:

- vocoder-based target-envelope carrier
- vocoder-based target-distribution carrier
- any other carrier that can fit edited mel or spectral targets more directly

Do not reopen:

- `LSF`
- `WORLD full resynthesis`
- old envelope-only routes
- old `WORLD-guided STFT delta` variants

unless a materially different synthesis surface is introduced.

### Phase 3. Start one minimal prototype

The first concrete prototype should be a minimal vocoder-based bridge from the
existing target representation into a new synthesis-safe carrier.

The prototype should be deliberately small:

- machine-only first
- fixed8 human pack second
- no broad route sweep before the first prototype proves perceptibility

## Next Allowed Action

The next allowed action is not another `LSF` sweep.

It is:

1. write the new synthesis-family requirement checkpoint
2. define the first vocoder-based carrier prototype
3. implement that prototype as a narrow machine-first experiment
