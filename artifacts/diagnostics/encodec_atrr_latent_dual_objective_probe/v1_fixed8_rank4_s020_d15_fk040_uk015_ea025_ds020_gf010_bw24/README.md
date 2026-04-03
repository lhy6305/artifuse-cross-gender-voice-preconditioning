# Encodec ATRR Latent Dual Objective Probe v1

- purpose: `single latent edit with masked delta-fit primary loss plus gap-adaptive distribution objectives`
- rows: `8`
- bandwidth_kbps: `24.0`
- delta_scale: `0.20`
- delta_cap_db: `1.50`
- distribution_scale: `0.20`
- rank: `4`
- steps: `30`
- lambda_frame_kl: `0.400`
- lambda_utt_kl: `0.150`
- lambda_energy_anchor: `0.250`
- gap_floor: `0.10`
- gap_power: `1.00`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_dual_objective_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_dual_objective_probe/v1_fixed8_rank4_s020_d15_fk040_uk015_ea025_ds020_gf010_bw24 `
  --bandwidth 24.0 `
  --delta-scale 0.20 `
  --delta-cap-db 1.50 `
  --distribution-scale 0.20 `
  --rank 4 `
  --steps 30 `
  --lr 0.0100 `
  --init-scale 0.0100 `
  --latent-cap 0.200 `
  --lambda-latent-l2 0.200 `
  --lambda-latent-time 0.100 `
  --lambda-wave-l1 1.000 `
  --lambda-frame-kl 0.400 `
  --lambda-utt-kl 0.150 `
  --lambda-energy-anchor 0.250 `
  --gap-floor 0.10 `
  --gap-power 1.00 `
  --core-mask `
  --core-mask-energy-threshold 0.60 `
  --core-mask-occupancy-threshold 0.35 `
  --core-mask-offcore-scale 0.00 `
  --core-mask-frame-threshold 0.60 `
  --core-mask-frame-occupancy-threshold 0.25 `
  --voiced-only
```
