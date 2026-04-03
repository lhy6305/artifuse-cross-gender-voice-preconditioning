# Encodec ATRR Latent Structured Probe v1

- purpose: `two-stage latent-side edit with target mover plus context compensator`
- rows: `8`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- target_rank: `4`
- target_steps: `30`
- target_cap: `0.200`
- context_rank: `2`
- context_steps: `20`
- context_cap: `0.080`
- lambda_context_null: `0.400`
- lambda_wave_l1: `1.000`
- voiced_only: `True`
- core_mask: `True`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_structured_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_structured_probe/v1_fixed8_tr4_ts30_tc020_tl020_tt010_cr2_cs20_cc008_cl025_ct012_cn040_w100_bw24 `
  --bandwidth 24.0 `
  --delta-scale 0.20 `
  --delta-cap-db 1.50 `
  --target-rank 4 `
  --target-steps 30 `
  --target-lr 0.0100 `
  --target-init-scale 0.0100 `
  --target-cap 0.200 `
  --lambda-target-l2 0.200 `
  --lambda-target-time 0.100 `
  --context-rank 2 `
  --context-steps 20 `
  --context-lr 0.0100 `
  --context-init-scale 0.0100 `
  --context-cap 0.080 `
  --lambda-context-l2 0.250 `
  --lambda-context-time 0.120 `
  --lambda-context-null 0.400 `
  --lambda-wave-l1 1.000 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.00 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
