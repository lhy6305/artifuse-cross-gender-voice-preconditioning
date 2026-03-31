# ATRR Vocoder Bridge Target Export v1

## Parameters

- core_step_size: `0.700`
- off_core_step_size: `0.200`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0200`

## Purpose

- This export is machine-only.
- It prepares edited target log-mel tensors for a future vocoder-based carrier.
- It does not synthesize audio by itself.

## Pack Summary

- rows: `8`
- avg simulated shift score: `58.42`
- avg simulated core coverage: `69.42`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`61.17` | coverage=`59.13` | export=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_bridge_target_export\v1_fixed8_v9a\targets\vctk__male__feminine__p226_011_mic1.npz`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`59.67` | coverage=`73.17` | export=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_bridge_target_export\v1_fixed8_v9a\targets\vctk__female__masculine__p231_011_mic1.npz`
- `stage0_speech_lsf_vctk_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`59.51` | coverage=`59.95` | export=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_bridge_target_export\v1_fixed8_v9a\targets\vctk__female__masculine__p230_107_mic1.npz`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`55.84` | coverage=`80.72` | export=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_bridge_target_export\v1_fixed8_v9a\targets\vctk__male__feminine__p241_005_mic1.npz`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`57.48` | coverage=`67.94` | export=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_bridge_target_export\v1_fixed8_v9a\targets\libritts_r__female__masculine__1995_1826_000022_000000.npz`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`57.57` | coverage=`79.85` | export=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_bridge_target_export\v1_fixed8_v9a\targets\libritts_r__female__masculine__1919_142785_000089_000003.npz`
