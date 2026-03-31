# P241 Single-Row Cap Sweep Nonmonotonicity v1

## Summary

This checkpoint records a single-row cap sweep on the current highest-priority
backend-instability row:

- `vctk male -> feminine`
- `p241_005_mic1`

The tested stack stayed fixed except for the pitch-correction cap:

- local `BigVGAN 22khz 80band 256x`
- backend-domain mel reconstruction
- explicit RMS matching
- bounded post-vocoder median-`F0` correction
- correction trigger: `150` cents

## Why This Probe Was Necessary

The previous weak-row diagnostics isolated `p241_005_mic1` as the clearest
backend-instability row still worth trying to save.

The immediate question was whether the bounded post-vocoder correction cap can
be tuned smoothly on that row.

If cap tuning behaved smoothly, the next route step could remain local cap
search.
If it behaved erratically, the route should stop spending time on blind cap
tuning and move to a different stabilization idea.

## Tested Variants

- baseline, no pitch correction
- cap `200`
- cap `250`
- cap `300`
- alternate backend check: `fmax8k` model with cap `300`

Outputs:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/p241_bigvgan_11025_rms_base/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/p241_bigvgan_11025_rms_pc150_cap200/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/p241_bigvgan_11025_rms_pc150_cap250/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/p241_bigvgan_11025_rms_pc150_cap300/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/p241_bigvgan_fmax8k_rms_pc150_cap300/`

## Result

Single-row comparison:

- baseline
  - shift: `17.72`
  - target EMD: `0.030263`
  - mel MAE: `0.494526`
  - `F0` drift: `904.94` cents
- cap `200`
  - shift: `53.12`
  - target EMD: `0.017243`
  - mel MAE: `0.976423`
  - `F0` drift: `770.00` cents
- cap `250`
  - shift: `8.93`
  - target EMD: `0.033499`
  - mel MAE: `1.010328`
  - `F0` drift: `560.00` cents
- cap `300`
  - shift: `26.83`
  - target EMD: `0.026914`
  - mel MAE: `1.039142`
  - `F0` drift: `320.00` cents
- `fmax8k` plus cap `300`
  - shift: `15.97`
  - target EMD: `0.030909`
  - mel MAE: `1.073691`
  - `F0` drift: `140.03` cents

## Reading Of The Result

The cap sweep is not monotonic on this row.

Important observations:

- `cap200` gives the strongest targetward movement on this row
- `cap300` reduces pitch drift much more strongly, but also gives weaker target
  movement than `cap200`
- `cap250` is worse than both neighboring settings on target shift
- switching to the `fmax8k` backend reduces pitch drift further, but does not
  recover targetward movement

This is enough to reject the idea that post-vocoder cap tuning is a smooth
one-dimensional control for this row.

## Route Decision

Do not keep spending route budget on blind cap sweeps for `p241_005_mic1`.

The row is still salvageable enough to remain interesting, but the next idea
should not be "try another nearby cap value".

## Immediate Next Step

The next stabilization experiment for `p241_005_mic1` should change the shape
of the stabilization, not just the size of the cap.

Candidates now worth considering are:

1. voiced-only or frame-selective correction instead of utterance-level median
   correction
2. pre-vocoder target-mel stabilization on the voiced region
3. a genuinely more `F0`-stable backend rather than another post-hoc cap tweak
