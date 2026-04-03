# Encodec ATRR Code Refit Probe v1

- purpose: `latent-teacher Encodec roundtrip anchor with hard native code-side refit`
- rows: `1`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- quantizer_range: `[24, 32)`
- teacher_rank: `4`
- teacher_steps: `30`
- teacher_lr: `0.0100`
- teacher_init_scale: `0.0100`
- teacher_latent_cap: `0.200`
- lambda_latent_l2: `0.200`
- lambda_latent_time: `0.100`
- lambda_wave_l1: `1.000`
- voiced_only: `True`
- core_mask: `True`
- core_mask_offcore_scale: `0.00`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_refit_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_code_refit_probe/smoke1 `
  --bandwidth 24.0 `
  --delta-scale 0.20 `
  --delta-cap-db 1.50 `
  --quantizer-start 24 `
  --quantizer-count 8 `
  --teacher-rank 4 `
  --teacher-steps 30 `
  --teacher-lr 0.0100 `
  --teacher-init-scale 0.0100 `
  --teacher-latent-cap 0.200 `
  --lambda-latent-l2 0.200 `
  --lambda-latent-time 0.100 `
  --lambda-wave-l1 1.000 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.00 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
