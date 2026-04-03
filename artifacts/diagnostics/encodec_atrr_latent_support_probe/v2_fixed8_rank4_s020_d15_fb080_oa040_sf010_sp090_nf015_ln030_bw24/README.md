# Encodec ATRR Latent Support Probe v1

- purpose: `single-stage latent edit with soft time-frequency support and off-support null regularization`
- rows: `8`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- rank: `4`
- steps: `30`
- frame_blend: `0.80`
- occupancy_anchor: `0.40`
- support_floor: `0.10`
- support_power: `0.90`
- null_floor: `0.15`
- lambda_null: `0.300`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_support_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_support_probe/v2_fixed8_rank4_s020_d15_fb080_oa040_sf010_sp090_nf015_ln030_bw24 `
  --bandwidth 24.0 `
  --delta-scale 0.20 `
  --delta-cap-db 1.50 `
  --rank 4 `
  --steps 30 `
  --lr 0.0100 `
  --init-scale 0.0100 `
  --latent-cap 0.200 `
  --lambda-latent-l2 0.200 `
  --lambda-latent-time 0.100 `
  --lambda-wave-l1 1.000 `
  --lambda-null 0.300 `
  --frame-blend 0.80 `
  --occupancy-anchor 0.40 `
  --support-floor 0.10 `
  --support-power 0.90 `
  --null-floor 0.15 `
  --voiced-only `
  --core-mask
```
