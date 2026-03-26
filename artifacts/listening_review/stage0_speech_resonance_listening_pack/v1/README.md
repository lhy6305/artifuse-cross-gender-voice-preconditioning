# Stage0 Speech Resonance Listening Pack v1

- purpose: `voiced broad-resonance tilt after envelope warp narrowing artifact`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_resonance_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_resonance_tilt_candidate_v1.json `
  --summary-csv tmp/stage0_speech_resonance_listening_pack/v1/listening_pack_summary.csv `
  --output-csv tmp/stage0_speech_resonance_listening_pack/v1/listening_review_queue.csv `
  --summary-md tmp/stage0_speech_resonance_listening_pack/v1/listening_review_quant_summary.md
```
