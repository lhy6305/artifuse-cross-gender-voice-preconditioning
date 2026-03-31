# Local BigVGAN Probe And Vocos Rejection v1

## Summary

This checkpoint records the first local external-model probe round after the
user downloaded the requested mel-native vocoder checkpoints into
`external_models/`.

Local model roots used in this round:

- `external_models/bigvgan_v2_22khz_80band_fmax8k_256x/`
- `external_models/bigvgan_v2_22khz_80band_256x/`
- `external_models/vocos-mel-24khz/`

These assets are confirmed to be ignored by Git through the active ignore
rules, so they are available for local probing without changing the repo asset
boundary.

## Local Availability Check

The following checks succeeded:

- local `BigVGAN` load from disk through `BigVGAN.from_pretrained(...)`
- local `Vocos` load from disk through `Vocos.from_hparams(...)`
- fixed8 target-package synthesis through the adapter script

This means the route is no longer blocked on remote model access for the two
downloaded backend families.

## Additional Adapter Correction

While integrating `Vocos`, one more adapter requirement became explicit.

The exported target packages currently store:

- utterance-level source and target distributions with `80` bins
- frame-level edited distributions with `80` bins

But external mel-native backends can require a different mel bin count.
`Vocos mel 24khz` requires `100` bins.

The adapter was therefore updated to resample frame-distribution bins into the
backend mel dimension before rebuilding backend-domain target mel.

Without this step, a backend with a different mel bin count cannot be judged
fairly.

## Vocos Result

Backend:

- `Vocos mel 24khz`

Smoke output:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_vocos_smoke2/`

Summary on 2 fixed8 rows:

- rows: `2`
- synthesis ok: `2`
- synthesis failed: `0`
- avg carrier target shift score: `0.00`
- avg target log-mel MAE: `4.7010`
- avg source probe self EMD: `0.042727`
- avg loudness drift: `-30.53 dB`
- avg `F0` drift: `1167.51 cents`

Reading:

- runnable
- local checkpoint usable
- clearly not a viable route candidate

The failure is not a pure integration bug anymore.
The backend can run, but source reconstruction fidelity and pitch stability are
far too weak for the active route.

## BigVGAN Result

Tested local variants:

- `bigvgan_v2_22khz_80band_fmax8k_256x`
- `bigvgan_v2_22khz_80band_256x`

Important practical note:

- explicit RMS matching materially improves comparison cleanliness for BigVGAN
- without RMS matching, loudness drift obscures backend reading

The strongest current result is:

- backend root: `external_models/bigvgan_v2_22khz_80band_256x/`
- output: `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_full8/`

Fixed8 full-pass summary:

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier target shift score: `30.60`
- avg target log-mel MAE: `0.4643`
- avg source probe self EMD: `0.010062`
- avg loudness drift: `0.00 dB`
- avg `F0` drift: `378.74 cents`

Strong rows reach:

- shift score up to `72.04`

Weak rows still fall to:

- shift score down to `0.17`
- `F0` drift up to `904.94 cents`

## Reading Of The BigVGAN Result

This is the best external neural carrier result seen so far on the active
route.

What is now clearly better than previous backends:

- local load is stable
- synthesis is stable across all fixed8 rows
- backend-domain mel reconstruction is clean
- source reconstruction fidelity is materially stronger than `WaveRNN` and
  `Vocos`
- loudness can be normalized away cleanly with explicit RMS matching
- multiple rows show meaningful targetward movement instead of collapse

What is still not good enough:

- average `F0` drift remains too large for human review
- row quality is still uneven across fixed8
- some rows are strong while others stay near identity or drift too far in
  pitch

The current unevenness is not random.
In this full8 pass, `LibriTTS` rows are materially stronger than `VCTK` rows,
while the weakest rows are both from `VCTK`.

So this backend is not approved for human review yet.
But unlike `Vocos`, it remains a valid active probe candidate.

## Route Decision

- Keep `Vocos mel 24khz` rejected for the active route.
- Keep `bigvgan_v2_22khz_80band_256x` as the provisional best local backend.
- Keep the route machine-only for now.
- Do not send BigVGAN output to human review yet.

## Immediate Next Step

The next work item is not another backend search pass.
The next work item is to analyze and reduce the remaining BigVGAN pitch drift
and row instability on fixed8 while keeping the current targetward movement.

The next bounded probe should therefore:

1. keep `bigvgan_v2_22khz_80band_256x` as the active backend
2. keep backend-domain mel reconstruction and RMS matching enabled
3. diagnose the worst `F0` drift rows by dataset, direction, and sample
4. test one narrow pitch-stability mitigation before any human pass
