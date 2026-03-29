# Stage0 Speech LSF Listening Pack masc_width_focus_v8b

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v8/configs/masc_width_focus_v8b.json `
  --output-dir artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/masc_width_focus_v8b
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v8/configs/masc_width_focus_v8b.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/masc_width_focus_v8b/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/masc_width_focus_v8b/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/masc_width_focus_v8b/listening_review_quant_summary.md
```
