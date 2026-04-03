# Encodec ATRR Filter Probe v1

- purpose: `source-preserving Encodec roundtrip anchor with narrow filter-side ATRR injection`
- rows: `1`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- keep_coeffs: `12`
- gain_floor_db: `-1.50`
- gain_cap_db: `1.50`
- voiced_only: `True`
- core_mask: `True`
- core_mask_offcore_scale: `0.00`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_filter_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_filter_probe/smoke1 `
  --bandwidth 24.0 `
  --delta-scale 0.20 `
  --delta-cap-db 1.50 `
  --keep-coeffs 12 `
  --gain-floor-db -1.50 `
  --gain-cap-db 1.50 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.00 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
