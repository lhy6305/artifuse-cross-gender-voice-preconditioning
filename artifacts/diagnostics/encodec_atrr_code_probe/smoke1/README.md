# Encodec ATRR Code Probe v1

- purpose: `source-preserving Encodec roundtrip anchor with local code-side ATRR injection`
- rows: `1`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- quantizer_range: `[24, 32)`
- neighbor_count: `4`
- rank: `4`
- steps: `30`
- lr: `0.0100`
- init_scale: `0.0100`
- identity_bias: `5.00`
- temperature: `1.00`
- lambda_code_l2: `0.200`
- lambda_code_time: `0.100`
- lambda_nonbase: `0.050`
- lambda_wave_l1: `1.000`
- voiced_only: `True`
- core_mask: `True`
- core_mask_offcore_scale: `0.00`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_code_probe/smoke1 `
  --bandwidth 24.0 `
  --delta-scale 0.20 `
  --delta-cap-db 1.50 `
  --quantizer-start 24 `
  --quantizer-count 8 `
  --neighbor-count 4 `
  --rank 4 `
  --steps 30 `
  --lr 0.0100 `
  --init-scale 0.0100 `
  --identity-bias 5.00 `
  --temperature 1.00 `
  --lambda-code-l2 0.200 `
  --lambda-code-time 0.100 `
  --lambda-nonbase 0.050 `
  --lambda-wave-l1 1.000 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.00 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
