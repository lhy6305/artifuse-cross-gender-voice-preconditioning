# Stage0 Rule Listening Quant Summary

- rows: `8`
- avg auto_quant_score: `70.51`
- avg auto_direction_score: `63.90`
- avg auto_preservation_score: `76.90`
- avg auto_effect_score: `74.74`

## Grade Counts

- `strong_pass`: `2`
- `pass`: `2`
- `borderline`: `0`
- `fail`: `4`

## Top Rows

- `stage0_speech_lpc_vctk_feminine_v1` | score=`94.00` | grade=`strong_pass` | notes=`rms_drift_gt_1p5db`
- `stage0_speech_lpc_vctk_feminine_v1` | score=`94.00` | grade=`strong_pass` | notes=`rms_drift_gt_1p5db`
- `stage0_speech_lpc_libritts_feminine_v1` | score=`93.48` | grade=`pass` | notes=`rms_drift_gt_1p5db`

## Risk Rows

- `stage0_speech_lpc_libritts_masculine_v1` | score=`45.91` | direction=`fail` | preserve=`borderline` | notes=`direction_weak;rms_drift_gt_1p5db`
- `stage0_speech_lpc_libritts_masculine_v1` | score=`34.38` | direction=`fail` | preserve=`borderline` | notes=`direction_weak;effect_subtle;rms_drift_gt_1p5db`
- `stage0_speech_lpc_vctk_masculine_v1` | score=`48.10` | direction=`fail` | preserve=`safe` | notes=`wrong_direction;rms_drift_gt_1p5db`
- `stage0_speech_lpc_vctk_masculine_v1` | score=`62.50` | direction=`fail` | preserve=`safe` | notes=`wrong_direction;rms_drift_gt_1p5db`
