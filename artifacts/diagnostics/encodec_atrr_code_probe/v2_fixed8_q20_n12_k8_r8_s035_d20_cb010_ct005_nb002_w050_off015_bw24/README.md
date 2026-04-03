# Encodec ATRR Code Probe v1

- purpose: `source-preserving Encodec roundtrip anchor with local code-side ATRR injection`
- rows: `8`
- bandwidth_kbps: `24.0`
- delta_scale: `0.35`
- delta_cap_db: `2.00`
- quantizer_range: `[20, 32)`
- neighbor_count: `8`
- rank: `8`
- steps: `40`
- lr: `0.0100`
- init_scale: `0.0150`
- identity_bias: `4.00`
- temperature: `1.00`
- lambda_code_l2: `0.100`
- lambda_code_time: `0.050`
- lambda_nonbase: `0.020`
- lambda_wave_l1: `0.500`
- voiced_only: `True`
- core_mask: `True`
- core_mask_offcore_scale: `0.15`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_code_probe/v2_fixed8_q20_n12_k8_r8_s035_d20_cb010_ct005_nb002_w050_off015_bw24 `
  --bandwidth 24.0 `
  --delta-scale 0.35 `
  --delta-cap-db 2.00 `
  --quantizer-start 20 `
  --quantizer-count 12 `
  --neighbor-count 8 `
  --rank 8 `
  --steps 40 `
  --lr 0.0100 `
  --init-scale 0.0150 `
  --identity-bias 4.00 `
  --temperature 1.00 `
  --lambda-code-l2 0.100 `
  --lambda-code-time 0.050 `
  --lambda-nonbase 0.020 `
  --lambda-wave-l1 0.500 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.15 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
