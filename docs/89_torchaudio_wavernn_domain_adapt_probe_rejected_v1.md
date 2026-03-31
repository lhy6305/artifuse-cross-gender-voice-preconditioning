# Torchaudio WaveRNN Domain-Adapt Probe Rejected v1

## Summary

This checkpoint records the first true mel-native neural vocoder attempt on the
active route.

Tested backend:

- `torchaudio` pretrained `WaveRNN`

Result:

- runnable
- mel-native
- still not a viable carrier for the route

## Why This Probe Was Necessary

After the local `RVC` posterior bridge was rejected, the next requirement was a
backend that is genuinely mel-native instead of a posterior-side bridge.

The local environment already had:

- `torchaudio`
- working downloads from `download.pytorch.org`
- a packaged pretrained `WaveRNN` bundle

So this was the narrowest available mel-native neural vocoder test.

## Important Frontend Correction

The first direct `WaveRNN` smoke test was not trustworthy, because it fed the
project-domain `target_log_mel` directly into a backend trained on a different
mel frontend.

The backend frontend requirements from the `torchaudio` bundle are:

- sample rate: `22050`
- `n_fft`: `2048`
- `win_length`: `1100`
- `hop_length`: `275`
- `mel_fmin`: `40`
- `mel_fmax`: `11025`

The adapter was therefore updated to rebuild source and target mel in the
backend's own frontend domain before synthesis.

This frontend correction is now part of the active route discipline for future
external mel-native backends.

## Domain-Adapted Smoke Result

Run output:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_wavernn_domainadapt_smoke2/`

Summary on 2 fixed8 rows:

- rows: `2`
- synthesis ok: `2`
- synthesis failed: `0`
- avg carrier target shift score: `26.05`
- avg target log-mel MAE: `2.2889`
- avg source probe self EMD: `0.039279`
- avg loudness drift: `3.42 dB`
- avg `F0` drift: `2375.01 cents`

One row partially recovered shift score after frontend correction.
The other row still collapsed to `0.00`.

## Reading Of The Result

The frontend correction mattered, but it did not fix the route-level problem.

What improved:

- the backend no longer looked purely broken for all rows
- at least one row showed a non-trivial target-shift score after domain
  adaptation

What still fails:

- `F0` preservation is catastrophically bad
- loudness drift is still too large
- mel reconstruction error is still far above the bounded baseline
- results are unstable across rows even in a 2-row smoke test

This is enough to reject the backend for the active route without spending a
full fixed8 run budget.

## Additional Integration Finding

An attempt was also made to move to a different external mel-native backend via
`transformers` and `SpeechT5HifiGan`.

That attempt did not reach model execution because repeated requests to
`huggingface.co` timed out in this environment.

This should be treated as an environment access issue, not as evidence for or
against that backend family.

## Route Decision

Do not continue with `torchaudio WaveRNN` as the active carrier candidate.

Do not spend a full fixed8 machine pass on it.

Do not send it to human review.

## Immediate Next Step

The next carrier task should require both of the following:

1. true mel-native synthesis
2. materially better pitch preservation than the current non-`F0`-aware backend

So the next practical target is not another generic `WaveRNN` retune.
It is a better external or dedicated vocoder integration with reliable model
access and stronger pitch stability.
