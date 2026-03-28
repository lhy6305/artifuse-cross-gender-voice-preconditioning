# Stage0 Speech LSF Listening Pack v2

- purpose: `lsf pair-shift residual-preserving probe after lpc pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lsf_listening_pack.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v2.json `
  --output-dir artifacts/listening_review/stage0_speech_lsf_listening_pack/v2
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v2.json `
  --summary-csv artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/listening_review_quant_summary.md
```
