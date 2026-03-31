# Local RVC Posterior Bridge Probe Rejected v1

## Summary

This checkpoint records the first `F0`-aware neural backend attempt after the
bounded Griffin-Lim carrier probe.

The tested backend was:

- local `RVC` pretrained `f0G48k` through a posterior-side bridge

Result:

- runnable
- machine measurable
- not a viable next carrier

## Implemented Asset

The active carrier adapter script now supports two backends:

- `griffinlim_mel_probe`
- `rvc_f0_posterior_bridge_v1`

The neural backend uses:

1. exported target `log-mel`
2. pseudo linear-spectrogram reconstruction
3. local `RVC` `enc_q -> dec` posterior bridge
4. source-side `F0` from the original waveform

## Why This Backend Was Worth Testing

The repo already had local `RVC` assets:

- config files
- `f0G48k` weights
- full generator architecture including `enc_q` and `dec`

So this was the narrowest available test of a local `F0`-aware neural carrier
without introducing a new external model family yet.

## Fixed8 Result

Run output:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_rvc_bridge/`

Summary:

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier target shift score: `15.89`
- avg target log-mel MAE: `2.3216`
- avg source probe self EMD: `0.029210`
- avg loudness drift: `7.93 dB`
- avg `F0` drift: `208.75 cents`

Worst behavior appeared on multiple `VCTK` rows where the carrier target shift
score collapsed to `0.00`.

## Comparison Against The Griffin-Lim Probe

The earlier bounded probe in `docs/87` was weak as a route candidate, but it
still provided a useful machine baseline.

Compared with that baseline, the local `RVC` posterior bridge is worse on the
main machine axes:

- shift score: `15.89` vs `56.21`
- target log-mel MAE: `2.3216` vs `0.3060`
- source probe self EMD: `0.029210` vs `0.005312`
- loudness drift: `7.93 dB` vs `-0.09 dB`
- `F0` drift: `208.75 cents` vs `108.13 cents`

So the local `RVC` posterior bridge is not a refinement of the current probe.
It is a clear regression.

## Reading Of The Failure

The negative result does not mean the carrier pivot itself was wrong.

It means this specific bridge is wrong:

- local generic `RVC` pretrained weights are not a suitable direct carrier for
  the exported target package boundary
- pseudo spectrogram inversion into the posterior encoder is too lossy
- the resulting synthesis drifts in loudness and `F0` while also moving away
  from the intended target distribution

## Route Decision

Do not continue broadening local `RVC` posterior-bridge variants.

Do not send this backend to human review.

Treat this backend as rejected for the active route.

## Immediate Next Step

The next carrier task should move to a true mel-native neural backend rather
than another local `RVC` bridge variant.

Preferred next boundary:

1. keep the exported target package format
2. plug in one real mel-to-wave neural carrier
3. require strong `F0` preservation and low loudness drift on fixed8 before
   any human pass

That means the next work item is an external or dedicated vocoder integration,
not more retuning of the local `RVC` posterior bridge.
