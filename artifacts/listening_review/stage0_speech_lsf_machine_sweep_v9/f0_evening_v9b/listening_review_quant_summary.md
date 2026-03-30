# Stage0 Rule Listening Quant Summary

- rows: `12`
- avg auto_quant_score: `66.03`
- avg auto_direction_score: `50.24`
- avg auto_preservation_score: `89.93`
- avg auto_effect_score: `65.76`

## Grade Counts

- `strong_pass`: `3`
- `pass`: `1`
- `borderline`: `5`
- `fail`: `3`

## Top Rows

- `stage0_speech_lsf_libritts_feminine_v8__low_f0_f0_evening_v9b` | score=`84.08` | grade=`strong_pass` | notes=`ok`
- `stage0_speech_lsf_libritts_masculine_v8__low_f0_f0_evening_v9b` | score=`83.58` | grade=`strong_pass` | notes=`presence_drop_gt_1p5db`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_f0_evening_v9b` | score=`80.50` | grade=`strong_pass` | notes=`presence_drop_gt_1p5db`

## Risk Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_f0_evening_v9b` | score=`49.31` | direction=`fail` | preserve=`safe` | notes=`direction_weak;effect_subtle`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_f0_evening_v9b` | score=`46.16` | direction=`fail` | preserve=`safe` | notes=`direction_weak`
- `stage0_speech_lsf_vctk_feminine_v8__high_f0_f0_evening_v9b` | score=`35.92` | direction=`fail` | preserve=`safe` | notes=`direction_weak;effect_subtle;rms_drift_gt_1p5db`
