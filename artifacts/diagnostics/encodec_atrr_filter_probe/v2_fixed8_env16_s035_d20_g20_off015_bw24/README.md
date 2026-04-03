# Encodec ATRR Filter Probe v1

- purpose: `source-preserving Encodec roundtrip anchor with narrow filter-side ATRR injection`
- rows: `8`
- bandwidth_kbps: `24.0`
- delta_scale: `0.35`
- delta_cap_db: `2.00`
- keep_coeffs: `16`
- gain_floor_db: `-2.00`
- gain_cap_db: `2.00`
- voiced_only: `True`
- core_mask: `True`
- core_mask_offcore_scale: `0.15`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_filter_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_filter_probe/v2_fixed8_env16_s035_d20_g20_off015_bw24 `
  --bandwidth 24.0 `
  --delta-scale 0.35 `
  --delta-cap-db 2.00 `
  --keep-coeffs 16 `
  --gain-floor-db -2.00 `
  --gain-cap-db 2.00 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.15 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
