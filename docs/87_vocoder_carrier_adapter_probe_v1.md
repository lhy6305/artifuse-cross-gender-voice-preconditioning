# Vocoder Carrier Adapter Probe v1

## Summary

This checkpoint records the first runnable carrier adapter after `LSF` route
closure.

The adapter boundary is now real, not just planned:

- exported `ATRR` target packages can be consumed by a mel-to-wave adapter
- the current backend is only a bounded probe
- the current backend is not acceptable as a route candidate yet

## Implemented Asset

The first carrier adapter script now exists:

- `scripts/run_atrr_vocoder_carrier_adapter.py`

Its current job is:

1. load one exported target `.npz`
2. synthesize probe waveforms from `source_log_mel` and `target_log_mel`
3. write waveform outputs
4. write a machine summary CSV and markdown report

Current run output:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_gl_probe/`

## Why Local RVC Assets Are Not The Direct Adapter

The local RVC codebase was inspected before building the adapter.

Result:

- the generator stack in `Retrieval-based-Voice-Conversion-WebUI-7ef1986`
  is not a direct match for the exported target package boundary

Reason:

- the RVC path expects Hubert-style content features
- it also expects pitch conditioning
- it also expects speaker conditioning
- it does not expose a simple standalone `edited_log_mel -> waveform` carrier

So the project should not pretend the local RVC generator can already serve as
the first direct carrier for the exported target packages.

## Current Probe Backend

The first backend is deliberately narrow:

- `griffinlim_mel_probe`

This backend is used only to validate the adapter boundary and machine metrics.

It is not a new main route by itself.
It is not a human-review candidate.

## Fixed8 Probe Result

The fixed8 probe ran on all 8 exported target packages.

Summary:

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier target shift score: `56.21`
- avg target log-mel MAE: `0.3060`
- avg source probe self EMD: `0.005312`
- avg loudness drift: `-0.09 dB`
- avg F0 drift: `108.13 cents`

Strongest rows by carrier target shift score:

- `vctk_corpus_0_92__p231__p231_011_mic1__986481509c` -> `67.25`
- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` -> `62.47`
- `vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f` -> `58.19`

Weakest rows:

- `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640` -> `47.24`
- `vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2` -> `49.91`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` -> `52.67`

## Reading Of The Result

The result gives one positive signal and one blocking signal.

Positive:

- the exported target packages are usable as the front half of a new carrier
- a simple mel-to-wave backend can preserve duration and loudness well enough
- the backend can partially move the synthesized output toward the target
  resonance distribution

Blocking:

- `F0` preservation is not good enough for the route
- average drift is over one semitone
- several rows drift far more than that

This means the current probe validates the carrier interface, but it does not
validate the current backend as a serious synthesis candidate.

## Route Decision After The Probe

Do not send this backend to human review.

Do not start a broad backend sweep yet.

The next step should be a single better carrier integration, not a large search.

## Immediate Next Step

The next implementation target should be:

1. keep the exported target package boundary as the front half
2. integrate one `F0`-aware neural carrier backend
3. rerun the same fixed8 machine probe with the new backend
4. gate any future human pass only after `F0` preservation and target-shift
   metrics both look materially better than this probe
