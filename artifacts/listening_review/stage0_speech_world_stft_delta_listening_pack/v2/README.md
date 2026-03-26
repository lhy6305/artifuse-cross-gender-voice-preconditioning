# Stage0 Speech WORLD-Guided STFT Delta Listening Pack v2

- purpose: `avoid WORLD resynthesis artifacts while keeping source-filter strength`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_world_stft_delta_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_world_stft_delta_candidate_v2.json `
  --summary-csv artifacts/listening_review/stage0_speech_world_stft_delta_listening_pack/v2/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_world_stft_delta_listening_pack/v2/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_world_stft_delta_listening_pack/v2/listening_review_quant_summary.md
```
