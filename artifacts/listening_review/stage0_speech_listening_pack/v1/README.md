# Stage0 Speech Listening Pack v1

- purpose: `speech-first audibility diagnostic`
- source: `experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv`
- selection: `dataset_name x source_gender` 每格取 `2` 条最接近该格中位 duration / f0 / centroid 的样本
- rows: `8`

## Composition

- `LibriTTS-R` / `female`: `2`
- `LibriTTS-R` / `male`: `2`
- `VCTK Corpus 0.92` / `female`: `2`
- `VCTK Corpus 0.92` / `male`: `2`

## Rebuild

```powershell
.\python.exe .\scripts\build_stage0_speech_listening_pack.py
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_rule_candidate_v1.json `
  --summary-csv artifacts/listening_review/stage0_speech_listening_pack/v1/listening_pack_summary.csv `
  --output-csv artifacts/listening_review/stage0_speech_listening_pack/v1/listening_review_queue.csv `
  --summary-md artifacts/listening_review/stage0_speech_listening_pack/v1/listening_review_quant_summary.md
```
