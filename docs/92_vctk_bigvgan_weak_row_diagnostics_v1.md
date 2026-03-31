# VCTK BigVGAN Weak Row Diagnostics v1

## Summary

This checkpoint records a targeted diagnostics pass on the remaining weak `VCTK`
rows under the current best machine-only stack:

- local `BigVGAN 22khz 80band 256x`
- backend-domain mel reconstruction
- explicit RMS matching
- bounded post-vocoder pitch correction

The goal was to separate two possible failure sources:

1. weak target packages before synthesis
2. backend instability added during synthesis

## Rows Examined

- `p230_107_mic1`
- `p231_011_mic1`
- `p226_011_mic1`
- `p241_005_mic1`

Reference stack output:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_pitchcorr150_cap300_full8/`

## Main Finding

The weak `VCTK` rows do not all fail for the same reason.

There are two different weak-row classes.

## Class A: Weakness Already Present In The Target Package

Rows:

- `p230_107_mic1`
- `p226_011_mic1`

Signals:

- source-target distribution distance is low compared with stronger `LibriTTS`
  rows
- package log-mel edit magnitude is also materially smaller than the stronger
  `LibriTTS` masculine rows

Observed values:

- `p230_107_mic1`
  - source-target EMD: `0.014656`
  - package log-mel delta: `0.5581`
  - final shift score: `4.47`
- `p226_011_mic1`
  - source-target EMD: `0.017215`
  - package log-mel delta: `0.9299`
  - final shift score: `7.12`

For comparison, stronger `LibriTTS` rows reach:

- source-target EMD around `0.0339` to `0.0457`
- package log-mel delta around `0.99` to `2.59`

Reading:

- these rows are weak before the backend is asked to synthesize them
- backend improvement alone may not be enough to make them strong

## Class B: Backend Instability Dominates

Rows:

- `p241_005_mic1`
- partly also `p230_107_mic1`

Signals:

- target package edit magnitude is not near zero
- bounded pitch correction improves shift versus the plain backend
- but pitch drift and mel mismatch remain too large

Observed values:

- `p241_005_mic1`
  - source-target EMD: `0.018391`
  - package log-mel delta: `0.8440`
  - plain backend shift: `17.72`
  - bounded-correction shift: `26.83`
  - bounded-correction `F0` drift: `320.00` cents
  - bounded-correction mel MAE: `1.0391`

Reading:

- this row is not only a weak-package problem
- backend instability still dominates the final outcome

## Strong Counterexample

`p231_011_mic1` shows the opposite pattern:

- source-target EMD: `0.019670`
- package log-mel delta: `0.9380`
- bounded-correction shift: `49.75`

This matters because it shows `VCTK` itself is not the only problem.
Some `VCTK` rows can move well enough under the current stack.

## Route Decision

The remaining weak rows should not be treated as one generic backend problem.

The active route now has two separate follow-up needs:

1. package-strength diagnostics for weak-package rows
2. backend-stability diagnostics for unstable rows

## Immediate Next Step

The next bounded experiment should prioritize backend-stability diagnostics on
`p241_005_mic1`, because that row still has enough target-package movement to be
worth saving.

In parallel, the route should not expect backend-only fixes to rescue
`p230_107_mic1` if the target package remains that weak.
