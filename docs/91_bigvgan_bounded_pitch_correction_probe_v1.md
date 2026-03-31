# BigVGAN Bounded Pitch Correction Probe v1

## Summary

This checkpoint records the first narrow pitch-stability mitigation test on top
of the current provisional best backend:

- backend root: `external_models/bigvgan_v2_22khz_80band_256x/`
- backend family: local mel-native `BigVGAN`
- baseline stack: backend-domain mel reconstruction plus explicit RMS matching

The purpose of this probe was not to open human review.
It was to test whether a bounded post-vocoder pitch correction layer can reduce
backend pitch drift without collapsing targetward movement.

## Why This Probe Was Necessary

The previous fixed8 full pass already showed that local `BigVGAN` is the best
backend tested so far, but it still had a route-level problem:

- average `F0` drift was too large for human review
- row quality was uneven
- the weakest rows were concentrated in `VCTK`

So the next bounded experiment needed to target pitch stability directly rather
than search for yet another backend family.

## Mitigation Variants

Three variants were compared on the same fixed8 set:

1. baseline `BigVGAN` plus RMS matching only
2. unrestricted median-`F0` correction after synthesis
3. bounded median-`F0` correction after synthesis

The bounded variant used:

- trigger threshold: `150` cents
- max correction magnitude: `300` cents

This means only clearly drifting rows are corrected, and no row is allowed to
take a large pitch-shift step in one post-processing pass.

## Result

Best bounded run output:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_pitchcorr150_cap300_full8/`

Bounded fixed8 summary:

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier target shift score: `36.70`
- avg target log-mel MAE: `1.0154`
- avg source probe self EMD: `0.010062`
- avg loudness drift: `0.00 dB`
- avg `F0` drift: `141.88 cents`

Baseline comparison:

- baseline avg carrier target shift score: `30.60`
- baseline avg target log-mel MAE: `0.4643`
- baseline avg `F0` drift: `378.74 cents`

## Reading Of The Result

The mitigation is directionally useful.

What improved:

- average `F0` drift dropped from `378.74` to `141.88` cents
- average target shift score improved from `30.60` to `36.70`
- loudness stayed clean because RMS matching remained stable
- the two worst large-drift `VCTK` rows no longer collapsed to near-zero shift

What did not fully resolve:

- target log-mel MAE more than doubled versus the baseline
- row quality is still uneven across fixed8
- `VCTK` remains weaker than `LibriTTS`
- the weakest row is still a `VCTK` masculine sample with near-identity shift

So this probe is a partial route improvement, not a route unlock.

## Important Negative Finding

The unrestricted median-`F0` correction variant should not be kept as the
active setting.

It reduced average `F0` drift even further, but it also over-corrected large
drift rows and could collapse target shift on some `VCTK` rows.

For this route, pitch correction must stay bounded.

## Route Decision

- Keep local `BigVGAN 22khz 80band 256x` as the active backend.
- Keep explicit RMS matching in the active stack.
- Keep bounded pitch correction as the current best mitigation shape.
- Do not send this stack to human review yet.

## Immediate Next Step

The next task is not another backend search pass and not human review.

The next task is a focused diagnostics pass on the remaining weak `VCTK` rows,
especially:

- `p230_107_mic1`
- `p226_011_mic1`
- `p241_005_mic1`

That pass should determine whether the remaining weakness is dominated by:

1. backend pitch instability
2. source-target mel rebuild mismatch on those rows
3. target package weakness already present before synthesis
