# ATRR Vocoder Carrier Adapter Probe v1

## Scope

- This run validates the carrier adapter boundary only.
- It is not a human-review candidate.
- The current backend is `rvc_f0_posterior_bridge_v1`.
- The local RVC generator stack is not a direct `edited_log_mel -> waveform` vocoder.
- The neural bridge backend therefore uses a posterior-side bridge through pseudo linear spectrograms plus source F0.

## Parameters

- backend: `rvc_f0_posterior_bridge_v1`
- griffinlim_iter: `64`
- n_fft: `2048`
- hop_length: `256`
- n_mels: `80`
- rvc_sid: `0`

## Pack Summary

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier_target_shift_score: `15.89`
- avg target_log_mel_mae: `2.3216`
- avg source_probe_self_emd: `0.029210`
- avg loudness_drift_db: `7.93`
- avg f0_drift_cents: `208.75`

## Strongest Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | shift=`42.64` | mel_mae=`2.189526` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_rvc_bridge\target_probe_wav\libritts_r__174__174_50561_000024_000000__d665dc2840__174_50561_000024_000000.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`38.29` | mel_mae=`2.104693` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_rvc_bridge\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | shift=`24.43` | mel_mae=`2.325148` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_rvc_bridge\target_probe_wav\libritts_r__2086__2086_149214_000006_000002__23f1c25eb7__2086_149214_000006_000002.wav`

## Weakest Rows

- `stage0_speech_lsf_vctk_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`2.549733` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_rvc_bridge\target_probe_wav\vctk_corpus_0_92__p230__p230_107_mic1__8330d16640__p230_107_mic1.wav`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`2.537404` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_rvc_bridge\target_probe_wav\vctk_corpus_0_92__p231__p231_011_mic1__986481509c__p231_011_mic1.wav`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`2.436718` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_rvc_bridge\target_probe_wav\vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f__p226_011_mic1.wav`
