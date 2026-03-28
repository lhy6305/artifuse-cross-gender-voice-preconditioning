# Stage0 Speech LSF Listening Pack order18_mid_focus_v2d

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v2/configs/order18_mid_focus_v2d.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v2/order18_mid_focus_v2d/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v2/order18_mid_focus_v2d/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v2/order18_mid_focus_v2d/listening_review_quant_summary.md
```
