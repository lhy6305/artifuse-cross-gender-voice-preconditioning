# Stage0 Speech LSF Listening Pack split_band_v4d

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v4/configs/split_band_v4d.json `
  --output-dir artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/split_band_v4d
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v4/configs/split_band_v4d.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/split_band_v4d/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/split_band_v4d/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/split_band_v4d/listening_review_quant_summary.md
```
