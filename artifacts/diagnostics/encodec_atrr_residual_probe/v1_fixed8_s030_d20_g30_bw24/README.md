# Encodec ATRR Residual Probe v1

- purpose: `source-preserving Encodec roundtrip anchor with narrow ATRR residual injection`
- rows: `8`
- bandwidth_kbps: `24.0`
- delta_scale: `0.30`
- delta_cap_db: `2.00`
- gain_floor_db: `-3.00`
- gain_cap_db: `3.00`
- voiced_only: `True`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_residual_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_residual_probe/v1_fixed8_s030_d20_g30_bw24 `
  --bandwidth 24.0 `
  --delta-scale 0.30 `
  --delta-cap-db 2.00 `
  --gain-floor-db -3.00 `
  --gain-cap-db 3.00 `
  --voiced-only
```
