# Stage0 Speech LSF Listening Pack air_preserve_v4a

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v4/configs/air_preserve_v4a.json `
  --output-dir artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/air_preserve_v4a
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v4/configs/air_preserve_v4a.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/air_preserve_v4a/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/air_preserve_v4a/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v4/air_preserve_v4a/listening_review_quant_summary.md
```
