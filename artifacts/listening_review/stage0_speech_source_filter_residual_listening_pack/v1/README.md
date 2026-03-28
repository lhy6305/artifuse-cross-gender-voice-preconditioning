# Stage0 Speech Source-Filter Residual Listening Pack v1

- purpose: `joint probe-guided envelope plus voiced harmonic residual probe after envelope-only exhaustion`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_source_filter_residual_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_source_filter_residual_candidate_v1.json `
  --summary-csv artifacts/listening_review/stage0_speech_source_filter_residual_listening_pack/v1/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_source_filter_residual_listening_pack/v1/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_source_filter_residual_listening_pack/v1/listening_review_quant_summary.md
```
