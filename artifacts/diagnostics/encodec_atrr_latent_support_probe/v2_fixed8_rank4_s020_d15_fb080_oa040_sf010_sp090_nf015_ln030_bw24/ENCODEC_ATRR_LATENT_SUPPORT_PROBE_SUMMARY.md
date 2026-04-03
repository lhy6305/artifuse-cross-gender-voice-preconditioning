# Encodec ATRR Latent Support Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- avg target_logmel_delta_l1_db: `0.0678`
- avg latent_delta_rms: `0.0075`
- avg latent_delta_abs_mean: `0.0042`
- avg final_fit_loss: `0.003320`
- avg final_null_loss: `0.000230`
- avg final_wave_l1: `0.000270`
- avg core_mask_ratio: `0.0609`
- avg fit_weight_mean: `0.0272`
- avg null_weight_mean: `0.5151`

## Strongest Latent Rows

- `libritts_r__174__174_50561_000024_000000__d665dc2840` | latent_rms=`0.010147` | fit_loss=`0.004970`
- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` | latent_rms=`0.008314` | fit_loss=`0.003386`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | latent_rms=`0.008260` | fit_loss=`0.003457`

## Widest Support Rows

- `vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2` | fit_weight_mean=`0.032336` | null_weight_mean=`0.417511`
- `vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f` | fit_weight_mean=`0.030514` | null_weight_mean=`0.459606`
- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` | fit_weight_mean=`0.029696` | null_weight_mean=`0.493106`
