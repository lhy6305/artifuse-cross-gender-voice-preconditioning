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

### `v1_fixed8_env12_s020_d15_g15_bw24`

- rows: `8`
- avg logmel_dtw_l1: `0.5806`
- avg mfcc_dtw_cosine: `0.0014`
- avg voiced_overlap_iou: `0.9108`
- avg f0_overlap_mae_cents: `12.1234`
- avg harmonic_share_delta: `-0.0231`
- avg mean_log_flatness_delta: `0.0659`
- avg zcr_delta: `-0.0011`
- avg structure_risk_score: `20.66`
- top risk records: `vctk_corpus_0_92__p231__p231_011_mic1__986481509c;vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2`

### `v2_fixed8_env16_s035_d20_g20_off015_bw24`

- rows: `8`
- avg logmel_dtw_l1: `0.6039`
- avg mfcc_dtw_cosine: `0.0016`
- avg voiced_overlap_iou: `0.9062`
- avg f0_overlap_mae_cents: `11.9993`
- avg harmonic_share_delta: `-0.0274`
- avg mean_log_flatness_delta: `0.0848`
- avg zcr_delta: `-0.0004`
- avg structure_risk_score: `22.16`
- top risk records: `vctk_corpus_0_92__p231__p231_011_mic1__986481509c;vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2`
