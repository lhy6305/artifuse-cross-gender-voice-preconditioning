# Stage0 Speech LSF Listening Pack masc_uniform_push_v2b

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/lsf_machine_sweep_v2/configs/masc_uniform_push_v2b.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v2/masc_uniform_push_v2b/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_machine_sweep_v2/masc_uniform_push_v2b/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_machine_sweep_v2/masc_uniform_push_v2b/listening_review_quant_summary.md
```
