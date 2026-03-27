# Stage0 Speech Neural Envelope Listening Pack v1

- purpose: `nonlinear / neural envelope latent probe`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_neural_envelope_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_neural_envelope_candidate_v1.json `
  --summary-csv artifacts/listening_review/stage0_speech_neural_envelope_listening_pack/v1/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_neural_envelope_listening_pack/v1/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_neural_envelope_listening_pack/v1/listening_review_quant_summary.md
```
