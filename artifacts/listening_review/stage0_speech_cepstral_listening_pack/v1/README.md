# Stage0 Speech Cepstral Listening Pack v1

- purpose: `low-order cepstral envelope edit probe after LPC pole-edit rejection`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_cepstral_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_cepstral_envelope_candidate_v1.json `
  --summary-csv artifacts/listening_review/stage0_speech_cepstral_listening_pack/v1/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_cepstral_listening_pack/v1/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_cepstral_listening_pack/v1/listening_review_quant_summary.md
```
