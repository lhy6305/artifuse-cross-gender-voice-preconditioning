# Representation Layer Probe v1

- purpose: `compare candidate tract/resonance representations before further editing work`
- input_csv: `experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv`
- rows: `48`

## Representations

- `world_mel`: WORLD cheaptrick 谱包络压到 mel bins 后做 voiced 平均
- `lpc_mel`: LPC 包络频响压到 mel bins 后做 voiced 平均
- `mfcc`: voiced 段 MFCC 平均，作为低阶 cepstral envelope proxy

## Top Separation Rows

- `VCTK Corpus 0.92` / `lpc_mel` | between=`0.013383` | sep_ratio=`1.232490`
- `VCTK Corpus 0.92` / `world_mel` | between=`0.000465` | sep_ratio=`0.546898`
- `LibriTTS-R` / `world_mel` | between=`0.000404` | sep_ratio=`0.499741`
- `VCTK Corpus 0.92` / `mfcc` | between=`0.001752` | sep_ratio=`0.462992`
- `LibriTTS-R` / `mfcc` | between=`0.001140` | sep_ratio=`0.312525`
- `LibriTTS-R` / `lpc_mel` | between=`0.002544` | sep_ratio=`0.175650`

## Notes

- 这个 probe 只回答表示是否稳定、是否携带性别相关分离度，不直接回答编辑是否有效。
- 下一步应基于 separation / continuity 结果，选择 1-2 条表示进入真正的编辑与重建阶段。
