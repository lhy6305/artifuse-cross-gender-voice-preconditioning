# Stage0 Speech Envelope Listening Pack v5

- purpose: `voiced-envelope-warp audibility probe after static EQ null result`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_envelope_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_envelope_warp_candidate_v5.json `
  --summary-csv artifacts/listening_review/stage0_speech_envelope_listening_pack/v5/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_envelope_listening_pack/v5/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_envelope_listening_pack/v5/listening_review_quant_summary.md
```
