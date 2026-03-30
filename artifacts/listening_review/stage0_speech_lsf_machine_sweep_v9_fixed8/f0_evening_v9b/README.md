# Stage0 Speech LSF Listening Pack f0_evening_v9b

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py `
  --input-csv experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv `
  --selection-manifest experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/configs/f0_evening_v9b.json `
  --output-dir artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/f0_evening_v9b
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/configs/f0_evening_v9b.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/f0_evening_v9b/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/f0_evening_v9b/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/f0_evening_v9b/listening_review_quant_summary.md
```
