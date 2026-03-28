# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `38.39`
- avg core_resonance_coverage_score: `46.28`
- avg over_localized_edit_penalty: `26.20`
- avg context_consistency_score: `44.74`
- avg frame_improvement_mean: `-0.004726`

## By Direction

### `feminine`

- avg shift score: `30.21`
- avg core coverage: `51.26`
- avg localization penalty: `26.78`
- avg context consistency: `41.27`
- avg frame improvement mean: `-0.008413`

### `masculine`

- avg shift score: `46.58`
- avg core coverage: `41.30`
- avg localization penalty: `25.62`
- avg context consistency: `48.21`
- avg frame improvement mean: `-0.001038`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_vctk_masculine_v7` | coverage=`30.05` | shift=`36.02` | localization_penalty=`26.42`
- `stage0_speech_lsf_libritts_masculine_v7` | coverage=`30.56` | shift=`45.31` | localization_penalty=`21.78`
- `stage0_speech_lsf_libritts_feminine_v7` | coverage=`36.83` | shift=`26.96` | localization_penalty=`17.98`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`16.41` | orig_target_emd=`0.018391` | proc_target_emd=`0.030748`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`26.96` | orig_target_emd=`0.032772` | proc_target_emd=`0.047873`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`35.77` | orig_target_emd=`0.045674` | proc_target_emd=`0.058677`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
