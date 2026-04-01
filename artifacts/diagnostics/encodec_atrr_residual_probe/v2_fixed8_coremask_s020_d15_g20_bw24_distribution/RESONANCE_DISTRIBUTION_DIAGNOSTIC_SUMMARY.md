# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.33`
- avg core_resonance_coverage_score: `58.00`
- avg over_localized_edit_penalty: `30.86`
- avg context_consistency_score: `48.51`
- avg frame_improvement_mean: `0.000120`

## By Direction

### `feminine`

- avg shift score: `39.56`
- avg core coverage: `54.92`
- avg localization penalty: `26.05`
- avg context consistency: `49.30`
- avg frame improvement mean: `0.001488`

### `masculine`

- avg shift score: `45.09`
- avg core coverage: `61.09`
- avg localization penalty: `35.67`
- avg context consistency: `47.72`
- avg frame improvement mean: `-0.001247`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`40.65` | shift=`49.50` | localization_penalty=`20.64`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`41.25` | shift=`49.97` | localization_penalty=`28.60`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`45.47` | shift=`49.87` | localization_penalty=`21.65`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`18.53` | orig_target_emd=`0.018391` | proc_target_emd=`0.029967`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`29.21` | orig_target_emd=`0.019670` | proc_target_emd=`0.027848`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`34.84` | orig_target_emd=`0.017215` | proc_target_emd=`0.022434`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
