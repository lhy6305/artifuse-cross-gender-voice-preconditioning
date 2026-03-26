# Stage0 Speech Formant Listening Pack v1

- purpose: `voiced adaptive formant-anchor morph after resonance tilt null result`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_formant_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_formant_anchor_candidate_v1.json `
  --summary-csv tmp/stage0_speech_formant_listening_pack/v1/listening_pack_summary.csv `
  --output-csv tmp/stage0_speech_formant_listening_pack/v1/listening_review_queue.csv `
  --summary-md tmp/stage0_speech_formant_listening_pack/v1/listening_review_quant_summary.md
```
