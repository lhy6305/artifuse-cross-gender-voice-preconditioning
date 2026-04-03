# Encodec ATRR Code Gate Probe v1

- purpose: `sparse native gate between base and teacher-directed codes`
- rows: `8`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- quantizer_range: `[24, 32)`
- teacher_rank: `4`
- teacher_steps: `30`
- gate_rank: `4`
- gate_steps: `30`
- gate_bias: `-2.00`
- gate_temperature: `1.00`
- lambda_gate_l2: `0.150`
- lambda_gate_time: `0.070`
- lambda_gate_mass: `0.020`
- lambda_wave_l1: `1.000`
- voiced_only: `True`
- core_mask: `True`
- core_mask_offcore_scale: `0.00`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_gate_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_code_gate_probe/v1_fixed8_q24_n8_tr4_ts30_gr4_gs30_gb200_gt100_gl015_gtm007_gg020_w100_bw24 `
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
  --gate-rank 4 `
  --gate-steps 30 `
  --gate-lr 0.0100 `
  --gate-init-scale 0.0100 `
  --gate-bias -2.00 `
  --gate-temperature 1.00 `
  --lambda-latent-l2 0.200 `
  --lambda-latent-time 0.100 `
  --lambda-gate-l2 0.150 `
  --lambda-gate-time 0.070 `
  --lambda-gate-mass 0.020 `
  --lambda-wave-l1 1.000 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.00 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
