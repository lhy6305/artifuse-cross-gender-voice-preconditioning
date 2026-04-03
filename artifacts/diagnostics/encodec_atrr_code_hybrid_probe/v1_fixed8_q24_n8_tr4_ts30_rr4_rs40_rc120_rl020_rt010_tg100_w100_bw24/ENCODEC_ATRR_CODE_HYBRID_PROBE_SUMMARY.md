# Encodec ATRR Code Hybrid Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- avg target_logmel_delta_l1_db: `0.0678`
- avg scaffold_teacher_gap_rms: `0.0351`
- avg residual_correction_rms: `0.0105`
- avg final_teacher_gap_rms: `0.0352`
- avg changed_code_ratio: `0.1531`
- avg teacher_final_mel_loss: `0.004490`
- avg teacher_final_wave_l1: `0.000350`
- avg final_mel_loss: `0.004898`
- avg final_wave_l1: `0.000994`
- avg core_mask_ratio: `0.0609`

## Strongest Residual Rows

- `libritts_r__174__174_50561_000024_000000__d665dc2840` | residual_rms=`0.012955` | final_gap_rms=`0.042624`
- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` | residual_rms=`0.012781` | final_gap_rms=`0.034577`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | residual_rms=`0.011873` | final_gap_rms=`0.042473`

## Closest To Teacher After Correction

- `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640` | final_gap_rms=`0.024757` | changed_code_ratio=`0.143750`
- `vctk_corpus_0_92__p231__p231_011_mic1__986481509c` | final_gap_rms=`0.029367` | changed_code_ratio=`0.152228`
- `vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2` | final_gap_rms=`0.030220` | changed_code_ratio=`0.135316`
