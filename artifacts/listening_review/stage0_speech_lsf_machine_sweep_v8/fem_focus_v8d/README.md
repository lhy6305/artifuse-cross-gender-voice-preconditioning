# Stage0 Speech LSF Listening Pack fem_focus_v8d

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v8/configs/fem_focus_v8d.json `
  --output-dir artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/fem_focus_v8d
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v8/configs/fem_focus_v8d.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/fem_focus_v8d/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/fem_focus_v8d/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/fem_focus_v8d/listening_review_quant_summary.md
```
