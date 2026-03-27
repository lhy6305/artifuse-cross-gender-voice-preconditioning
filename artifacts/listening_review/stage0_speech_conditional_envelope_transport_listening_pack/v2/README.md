# Stage0 Speech Conditional Envelope Transport Listening Pack v2

- purpose: `content-and-f0-conditioned reference envelope transport probe`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_conditional_envelope_transport_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_conditional_envelope_transport_candidate_v2.json `
  --summary-csv artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v2/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v2/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v2/listening_review_quant_summary.md
```
