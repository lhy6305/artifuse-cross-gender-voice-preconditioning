# Stage0 Rule Listening Quant Summary

- rows: `8`
- avg auto_quant_score: `58.45`
- avg auto_direction_score: `31.19`
- avg auto_preservation_score: `97.80`
- avg auto_effect_score: `60.29`

## Grade Counts

- `strong_pass`: `1`
- `pass`: `0`
- `borderline`: `2`
- `fail`: `5`

## Top Rows

- `stage0_speech_envwarp_vctk_feminine_v4` | score=`86.50` | grade=`strong_pass` | notes=`ok`
- `stage0_speech_envwarp_vctk_feminine_v4` | score=`80.82` | grade=`borderline` | notes=`ok`
- `stage0_speech_envwarp_vctk_masculine_v4` | score=`70.13` | grade=`borderline` | notes=`ok`

## Risk Rows

- `stage0_speech_envwarp_libritts_masculine_v4` | score=`35.90` | direction=`fail` | preserve=`safe` | notes=`wrong_direction;effect_subtle`
- `stage0_speech_envwarp_libritts_masculine_v4` | score=`41.63` | direction=`fail` | preserve=`safe` | notes=`wrong_direction;rms_drift_gt_1p5db`
- `stage0_speech_envwarp_libritts_feminine_v4` | score=`40.38` | direction=`fail` | preserve=`safe` | notes=`wrong_direction`
- `stage0_speech_envwarp_libritts_feminine_v4` | score=`65.34` | direction=`fail` | preserve=`safe` | notes=``
- `stage0_speech_envwarp_vctk_masculine_v4` | score=`46.90` | direction=`fail` | preserve=`safe` | notes=`direction_weak`
