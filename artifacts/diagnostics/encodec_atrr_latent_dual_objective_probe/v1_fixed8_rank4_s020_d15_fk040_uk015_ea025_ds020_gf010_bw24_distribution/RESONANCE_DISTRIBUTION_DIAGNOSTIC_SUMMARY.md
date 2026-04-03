# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `41.92`
- avg core_resonance_coverage_score: `57.89`
- avg over_localized_edit_penalty: `31.92`
- avg context_consistency_score: `56.45`
- avg frame_improvement_mean: `0.001670`

## By Direction

### `feminine`

- avg shift score: `38.27`
- avg core coverage: `52.74`
- avg localization penalty: `28.17`
- avg context consistency: `54.21`
- avg frame improvement mean: `0.001513`

### `masculine`

- avg shift score: `45.58`
- avg core coverage: `63.03`
- avg localization penalty: `35.67`
- avg context consistency: `58.69`
- avg frame improvement mean: `0.001826`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`36.31` | shift=`50.23` | localization_penalty=`21.65`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`39.11` | shift=`51.73` | localization_penalty=`18.22`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`40.13` | shift=`53.68` | localization_penalty=`20.61`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.49` | orig_target_emd=`0.018391` | proc_target_emd=`0.031085`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`26.90` | orig_target_emd=`0.019670` | proc_target_emd=`0.028757`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.16` | orig_target_emd=`0.017215` | proc_target_emd=`0.023359`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
