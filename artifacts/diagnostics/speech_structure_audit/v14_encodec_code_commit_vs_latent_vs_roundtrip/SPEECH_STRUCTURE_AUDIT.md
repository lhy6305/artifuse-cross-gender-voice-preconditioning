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

### `v1_fixed8_rank4_s020_d15_lc020_lt010_w100_bw24`

- rows: `8`
- avg logmel_dtw_l1: `0.5360`
- avg mfcc_dtw_cosine: `0.0011`
- avg voiced_overlap_iou: `0.9340`
- avg f0_overlap_mae_cents: `7.8395`
- avg harmonic_share_delta: `-0.0130`
- avg mean_log_flatness_delta: `0.0217`
- avg zcr_delta: `-0.0024`
- avg structure_risk_score: `17.56`
- top risk records: `vctk_corpus_0_92__p231__p231_011_mic1__986481509c;vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2;vctk_corpus_0_92__p230__p230_107_mic1__8330d16640`

### `v1_fixed8_q24_n8_tr4_ts30_cr4_cs30_cb000_ct050_cl015_ctm007_cm010_w100_bw24`

- rows: `8`
- avg logmel_dtw_l1: `0.5367`
- avg mfcc_dtw_cosine: `0.0011`
- avg voiced_overlap_iou: `0.9362`
- avg f0_overlap_mae_cents: `7.8787`
- avg harmonic_share_delta: `-0.0138`
- avg mean_log_flatness_delta: `0.0227`
- avg zcr_delta: `-0.0024`
- avg structure_risk_score: `17.52`
- top risk records: `vctk_corpus_0_92__p231__p231_011_mic1__986481509c;vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2;vctk_corpus_0_92__p230__p230_107_mic1__8330d16640`
