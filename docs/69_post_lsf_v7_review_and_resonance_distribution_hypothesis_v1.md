# Post LSF v7 Review And Resonance Distribution Hypothesis v1

## Review Result

Formal human review for `LSF v7` is now complete.

Queue file:

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v7/listening_review_queue.csv`

Pack-level review summary:

- `rows = 8`
- `effect_audible = yes 7 / maybe 1 / no 0`
- `strength_fit = too_weak 8 / 8`
- `direction_correct = maybe 8 / 8`
- `artifact_issue = empty 8 / 8`

## Interpretation

`v7` confirms a narrower result than `v6`.

What improved:

- the pack is now consistently audible
- the pack is not failing because of obvious artifacts

What still failed:

- the pack is still uniformly too weak
- the direction remains uncertain rather than clearly correct

## User Qualitative Note

In addition to the exported queue fields, the user reported a more specific subjective diagnosis:

- the change is still too weak
- the core resonance does not appear to move

This note is important because it narrows the likely failure mode further than a generic weak-effect label.

## Route Decision

The `LSF` route is not closed yet, but the current partial-band geometry approach is no longer a sufficient default next step.

The next working hypothesis is:

- the target is not a small set of isolated band moves
- the target is a broader resonance-distribution change across the full spectral envelope
- the method must affect the core resonance pattern, not only peripheral brightness or selected low-order geometry terms

## Next Technical Direction

The next route discussion should test a distributional resonance view instead of another simple strength bump.

That means treating resonance as a structured distribution over:

- frequency
- time
- voiced harmonic support
- phonetic or vowel context

instead of treating it as a small edit to only a few local bands or pair parameters.
