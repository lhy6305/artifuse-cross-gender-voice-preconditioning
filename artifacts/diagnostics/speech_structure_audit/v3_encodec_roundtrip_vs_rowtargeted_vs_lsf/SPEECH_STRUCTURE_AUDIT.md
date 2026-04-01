# Speech Structure Audit v1

## Scope

- This audit measures source-to-processed structural distortion directly.
- It is designed for packs where target-resonance judgment is blocked by audible synthesis artifacts.

## Pack Summary

### `v1_fixed8_bw24`

- rows: `8`
- avg logmel_dtw_l1: `0.5361`
- avg mfcc_dtw_cosine: `0.0011`
- avg voiced_overlap_iou: `0.9149`
- avg f0_overlap_mae_cents: `11.4966`
- avg harmonic_share_delta: `-0.0136`
- avg mean_log_flatness_delta: `0.0230`
- avg zcr_delta: `-0.0024`
- avg structure_risk_score: `18.39`
- top risk records: `vctk_corpus_0_92__p231__p231_011_mic1__986481509c;vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2`

### `stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1`

- rows: `8`
- avg logmel_dtw_l1: `0.7188`
- avg mfcc_dtw_cosine: `0.0041`
- avg voiced_overlap_iou: `0.7450`
- avg f0_overlap_mae_cents: `77.9540`
- avg harmonic_share_delta: `-0.0586`
- avg mean_log_flatness_delta: `-0.6190`
- avg zcr_delta: `-0.0020`
- avg structure_risk_score: `31.01`
- top risk records: `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9;libritts_r__1995__1995_1826_000022_000000__82d5a66723`

### `stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a`

- rows: `8`
- avg logmel_dtw_l1: `0.3257`
- avg mfcc_dtw_cosine: `0.0012`
- avg voiced_overlap_iou: `0.9453`
- avg f0_overlap_mae_cents: `6.3389`
- avg harmonic_share_delta: `-0.0177`
- avg mean_log_flatness_delta: `-0.0104`
- avg zcr_delta: `-0.0003`
- avg structure_risk_score: `12.37`
- top risk records: `libritts_r__1919__1919_142785_000089_000003__11e66c65d9;libritts_r__1995__1995_1826_000022_000000__82d5a66723;libritts_r__174__174_50561_000024_000000__d665dc2840`
