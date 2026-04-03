# Encodec ATRR Latent Distribution Probe v1

- purpose: `source-preserving Encodec latent edit with frame-distribution and utterance-distribution objectives`
- rows: `1`
- bandwidth_kbps: `24.0`
- distribution_scale: `0.35`
- rank: `4`
- steps: `30`
- lambda_frame_kl: `1.000`
- lambda_utt_kl: `0.500`
- lambda_energy_anchor: `0.500`
- lambda_wave_l1: `1.000`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_distribution_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --target-dir artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/targets `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_distribution_probe/smoke1 `
  --bandwidth 24.0 `
  --distribution-scale 0.35 `
  --rank 4 `
  --steps 30 `
  --lr 0.0100 `
  --init-scale 0.0100 `
  --latent-cap 0.200 `
  --lambda-frame-kl 1.000 `
  --lambda-utt-kl 0.500 `
  --lambda-energy-anchor 0.500 `
  --lambda-latent-l2 0.200 `
  --lambda-latent-time 0.100 `
  --lambda-wave-l1 1.000 `
  --voiced-only
```
