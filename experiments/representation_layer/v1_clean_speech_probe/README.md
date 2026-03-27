# Representation Layer Probe v1

- purpose: `compare candidate tract/resonance representations before further editing work`
- input_csv: `data/datasets/_meta/utterance_manifest_clean_speech_v1.csv`
- rows: `128`

## Representations

- `world_mel`: WORLD cheaptrick 谱包络压到 mel bins 后做 voiced 平均
- `lpc_mel`: LPC 包络频响压到 mel bins 后做 voiced 平均
- `mfcc`: voiced 段 MFCC 平均，作为低阶 cepstral envelope proxy

## Top Separation Rows

- `LibriTTS-R` / `lpc_mel` | between=`0.048493` | sep_ratio=`7.287961`
- `LibriTTS-R` / `mfcc` | between=`0.004340` | sep_ratio=`1.949318`
- `LibriTTS-R` / `world_mel` | between=`0.000721` | sep_ratio=`1.391159`
- `VCTK Corpus 0.92` / `mfcc` | between=`0.005644` | sep_ratio=`1.373142`
- `VCTK Corpus 0.92` / `world_mel` | between=`0.001252` | sep_ratio=`1.107496`
- `VCTK Corpus 0.92` / `lpc_mel` | between=`0.011574` | sep_ratio=`0.810861`

## Notes

- 这个 probe 只回答表示是否稳定、是否携带性别相关分离度，不直接回答编辑是否有效。
- 下一步应基于 separation / continuity 结果，选择 1-2 条表示进入真正的编辑与重建阶段。
