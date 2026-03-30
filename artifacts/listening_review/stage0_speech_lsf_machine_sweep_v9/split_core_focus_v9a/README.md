# Stage0 Speech LSF Listening Pack split_core_focus_v9a

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `12`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py `
  --input-csv experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv `
  --samples-per-cell 3 `
  --selection-mode f0_span `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/configs/split_core_focus_v9a.json `
  --output-dir artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9/split_core_focus_v9a
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/configs/split_core_focus_v9a.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9/split_core_focus_v9a/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9/split_core_focus_v9a/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9/split_core_focus_v9a/listening_review_quant_summary.md
```
