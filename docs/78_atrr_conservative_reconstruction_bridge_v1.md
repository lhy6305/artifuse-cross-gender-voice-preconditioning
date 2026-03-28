# ATRR Conservative Reconstruction Bridge v1

## Purpose

This document defines the first conservative reconstruction bridge from `ATRR` distribution-space edits back to audio.

The goal is not to build a final listening pack immediately.
The goal is to choose the shortest stable path from:

- edited resonance-distribution targets

to:

- synthesis-safe audio suitable for machine-only checks

## Reconstruction Decision

The focused `ATRR` sweep is now strong enough to justify reconstruction planning.

The first reconstruction bridge should use:

- a stable `LSF` carrier as the primary route

and keep:

- the existing cepstral phase-preserving path only as a fallback diagnostic route

## Why The Primary Carrier Should Stay `LSF`

The repo already has a stable voiced-frame carrier path in:

- `scripts/build_stage0_speech_lsf_listening_pack.py`

That path already provides:

- stable `LPC -> LSF -> LPC` conversion
- spacing constraints
- original residual preservation
- overlap-add synthesis
- loudness and peak normalization

This is the shortest conservative bridge because it reuses a synthesis path that is already known to produce machine-viable audio.

## Why Cepstral Should Stay Secondary

The repo also has a usable phase-preserving envelope carrier in:

- `scripts/build_stage0_speech_cepstral_listening_pack.py`

That route is easier to fit in pure envelope space, but it is less aligned with the current residual-preserving `LSF` main line.

The cepstral path should therefore be used only when:

- the `LSF` fit becomes unstable
- or a machine-only comparison is needed to separate carrier-fit failure from target-definition failure

## Reconstruction Objects

For each voiced frame:

1. build source `ATRR` distribution object `x_t`
2. build edited target distribution `y_t`
3. recover a smooth target log-envelope in analysis space
4. fit that target envelope onto a stable `LSF` carrier
5. resynthesize using the original residual path

The carrier is not the edit object.
The carrier is only the constrained synthesis surface.

## Proposed Primary Bridge

### Stage 1. Reuse existing voiced-frame analysis

Use the same frame structure already present in the `LSF` path:

- voiced-frame gating
- `stable_lpc`
- `lpc_to_lsf`
- original residual extraction

This preserves continuity with the current route and keeps the reconstruction boundary small.

### Stage 2. Build a bounded target log-envelope

The simulator currently edits a gain-normalized distribution on a perceptual axis.

For reconstruction, convert `y_t` into a bounded smooth target log-envelope:

- keep the source frame loudness anchor
- keep the source high-band shape when the target delta is weak
- cap per-bin target movement with the chosen `ATRR` parameter band

The first reconstruction pass should center on:

- `core_step_size = 0.50` to `0.55`
- `off_core_step_size = 0.15`
- `frame_smoothness_weight = 0.30`
- `max_bin_step = 0.0085` to `0.0100`

### Stage 3. Fit target envelope onto a stable `LSF` carrier

The first fit should be local and conservative.

Do not solve a large unconstrained inverse problem.

Instead:

- start from the original frame `LSF`
- search only a bounded neighborhood around that `LSF`
- minimize weighted mismatch between the carrier envelope and the target log-envelope
- keep explicit penalties for:
  - `LSF` displacement size
  - spacing violations
  - high-band collapse
  - low-value off-core movement

The fit objective should weight:

- core-support bins more strongly
- off-core bins less strongly
- the source high band enough to prevent generic darkening

### Stage 4. Reuse the existing residual-preserving synthesis path

Once the edited carrier is found:

- convert edited `LSF -> LPC`
- extract the original residual with the original `LPC`
- filter that residual through the edited `LPC`
- keep the existing RMS and peak normalization logic

This should reuse the same conservative synthesis skeleton already in the current `LSF` script.

## Fitting Strategy

The first implementation should avoid a fully continuous optimizer.

Use a bounded projected search first.

Recommended first fit surface:

- paired `LSF` center moves
- paired width moves
- optional low-order smooth correction on remaining poles

This keeps the first bridge close to the current stable route while allowing the target envelope to influence the fit more directly than the old handcrafted rule family.

## Fallback Diagnostic Route

If the `LSF` fit fails too often on voiced frames, do not immediately abandon the target definition.

Instead:

1. project the same target log-envelope into the existing cepstral carrier
2. synthesize through the phase-preserving cepstral path
3. compare machine metrics against the `LSF` carrier result

Interpretation:

- if cepstral succeeds while `LSF` fails, the problem is likely carrier fitting
- if both fail, the problem is more likely the edited target itself

## Machine-Only Reconstruction Checks

Before any listening pack work, the first reconstruction pass must report:

- voiced-frame carrier fit success rate
- voiced-frame fallback rate
- mean target-envelope fit error
- mean core-bin fit error
- high-band preservation error
- reconstructed resonance-distribution shift score
- reconstructed core-resonance coverage score
- reconstructed localization penalty
- reconstructed frame improvement mean
- existing artifact proxies
- existing presence and brilliance preservation checks
- existing `F0` and voiced-structure preservation checks

## Minimum Acceptance Rule

The first reconstruction candidate band is acceptable only if all of the following hold:

- the voiced-frame fit succeeds on most frames
- reconstruction keeps the `ATRR` diagnostic advantage over observed `v7`
- artifact proxies do not collapse
- presence and brilliance do not regress into the old muffled failure mode
- `F0` and voiced structure stay near the original frame track

## File-Level Implementation Direction

The first implementation should extend the existing `LSF` script family rather than start from a blank audio method.

Primary code anchor:

- `scripts/build_stage0_speech_lsf_listening_pack.py`

Secondary diagnostic fallback anchor:

- `scripts/build_stage0_speech_cepstral_listening_pack.py`

Diagnostic scorer reuse:

- `scripts/extract_resonance_distribution_diagnostics.py`
- `scripts/simulate_targetward_resonance_residual.py`

## Immediate Next Step

The next implementation task should be:

- add a machine-only `ATRR -> LSF carrier` reconstruction prototype

The first prototype should emit:

- per-row reconstruction summaries
- fit diagnostics
- reconstructed audio only for machine scoring

No new human listening pack should be built until that machine-only reconstruction prototype is scored.
