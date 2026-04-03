# Encodec ATRR Code Hybrid Probe v1

- purpose: `hard native code scaffold plus bounded continuous residual correction`
- rows: `1`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- quantizer_range: `[24, 32)`
- teacher_rank: `4`
- teacher_steps: `30`
- residual_rank: `4`
- residual_steps: `40`
- residual_cap: `0.120`
- lambda_residual_l2: `0.200`
- lambda_residual_time: `0.100`
- lambda_teacher_gap: `1.000`
- lambda_wave_l1: `1.000`
- voiced_only: `True`
- core_mask: `True`
- core_mask_offcore_scale: `0.00`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_hybrid_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_code_hybrid_probe/smoke2_rc120_tg100_rs40 `
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
  --residual-rank 4 `
  --residual-steps 40 `
  --residual-lr 0.0100 `
  --residual-init-scale 0.0100 `
  --residual-cap 0.120 `
  --lambda-residual-l2 0.200 `
  --lambda-residual-time 0.100 `
  --lambda-teacher-gap 1.000 `
  --lambda-wave-l1 1.000 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.00 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
