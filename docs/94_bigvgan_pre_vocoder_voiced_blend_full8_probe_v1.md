# BigVGAN Pre Vocoder Voiced Blend Full8 Probe v1

## Summary

This checkpoint records the first full8 result after changing stabilization
shape instead of continuing blind post-vocoder cap tuning.

The new stack is:

- local `BigVGAN 22khz 80band 256x`
- backend-domain mel reconstruction
- explicit RMS matching
- voiced-only pre-vocoder target-log-mel blend
- post-vocoder median-`F0` correction with trigger `150` cents and cap `200`

The tested voiced blend setting is:

- `voiced_target_blend_alpha = 0.75`

## Why This Probe Was Necessary

The previous `p241_005_mic1` single-row cap sweep showed that nearby
post-vocoder cap values are nonmonotonic.

That meant the next useful experiment had to change stabilization shape.

Two candidates were tested next on `p241_005_mic1`:

1. voiced-only post-vocoder correction
2. voiced-only pre-vocoder target-log-mel blending

The voiced-only post-vocoder correction variant did not improve the row-level
tradeoff enough.

The pre-vocoder voiced blend did.

So the first route-worthy extension was a full fixed8 pass with the pre-vocoder
blend stack.

## Single-Row Gate Signal

On `p241_005_mic1`, the new stack reached:

- shift: `34.70`
- target log-mel MAE: `0.425003`
- `F0` drift: `30.00` cents

This was the first version of that row that improved all three of the route's
practical priorities at the same time:

- materially better targetward movement than the plain backend
- much lower pitch drift than previous post-vocoder-only variants
- lower mel error than the old post-vocoder cap variants

## Full8 Result

Run output:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8/`

Summary:

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier target shift score: `40.84`
- avg target log-mel MAE: `0.7197`
- avg source probe self EMD: `0.010062`
- avg loudness drift: `0.00 dB`
- avg `F0` drift: `156.87` cents

## Comparison To Previous Best Full8 Stack

Previous best stack:

- bounded post-vocoder correction only
- output:
  `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_pitchcorr150_cap300_full8/`

Comparison:

- shift score: `36.70 -> 40.84`
- target log-mel MAE: `1.0154 -> 0.7197`
- `F0` drift: `141.88 -> 156.87`

Reading:

- targetward movement improved
- mel reconstruction improved materially
- pitch drift regressed slightly versus the previous bounded-cap stack, but
  stayed far below the plain backend and far below the old unstable rows

This is a better overall full8 tradeoff than the previous active stack.

## Important Row-Level Reading

The new stack materially improves multiple previously weak rows:

- `p230_107_mic1`: `0.17 -> 27.96`
- `p226_011_mic1`: `7.12 -> 32.75`
- `p241_005_mic1`: `17.72 -> 34.70`

It also preserves or improves several stronger rows while avoiding the very
large mel penalties of the old bounded-cap-only stack.

Not every row improved on every metric.
For example, one stronger `LibriTTS` feminine row lost some shift while another
`LibriTTS` feminine row still carried higher pitch drift than desired.

But the full-pack reading is still clearly positive.

## Route Decision

The new active stack is now:

- local `BigVGAN 22khz 80band 256x`
- backend-domain mel reconstruction
- explicit RMS matching
- voiced-only pre-vocoder target-log-mel blend with alpha `0.75`
- post-vocoder median-`F0` correction with trigger `150` and cap `200`

This replaces the previous bounded-cap-only stack as the current best machine
candidate.

## Immediate Next Step

The route is no longer blocked on the old `p241` instability.

The next task should be one of the following:

1. treat this stack as the first machine-credible human-review candidate and
   prepare a fixed8 listening pack
2. if one more machine pass is preferred first, target the remaining
   higher-drift `LibriTTS` feminine row without regressing the rescued `VCTK`
   rows
