# Stage0 Speech LPC Listening Pack v2

- purpose: `lpc residual-preserving pole edit probe after representation-layer pivot`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_lpc_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_lpc_resonance_candidate_v2.json `
  --summary-csv artifacts/listening_review/stage0_speech_lpc_listening_pack/v2/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_lpc_listening_pack/v2/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_lpc_listening_pack/v2/listening_review_quant_summary.md
```
