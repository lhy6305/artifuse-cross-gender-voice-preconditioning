# Stage0 Speech VTL Warping Listening Pack v1

- purpose: `tract-length warp on WORLD envelope with original-phase reconstruction after LSF setback`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_vtl_warping_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_vtl_warping_candidate_v1.json `
  --summary-csv artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/listening_review_quant_summary.md
```
