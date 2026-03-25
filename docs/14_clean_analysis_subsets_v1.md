# clean analysis subsets v1

## 目标

为阶段 0/1 提供一版保守、可复现、可直接开跑的主分析输入，而不是一上来把全部样本混在一起。

## 输出文件

- `data/datasets/_meta/utterance_manifest_clean_speech_v1.csv`
- `data/datasets/_meta/utterance_manifest_clean_singing_v1.csv`
- `data/datasets/_meta/clean_subset_summary_v1.csv`

## clean_speech_v1 规则

- 数据来源仅限：
  - `VCTK Corpus 0.92`
  - `LibriTTS-R`
- 过滤条件：
  - `domain == speech`
  - `quality_flag == ok`
  - `gender in {male, female}`
  - `language == English`
  - `duration_sec` 在 `2` 到 `20` 秒之间
- 平衡策略：
  - 按 `(dataset_name, gender)` 划分四个 cell
  - 以最小 cell 大小为目标，当前是每个 cell `3775` 条
  - cell 内按 `speaker_id` 做 round-robin，降低单个说话人支配

## clean_singing_v1 规则

- 数据来源仅限 `VocalSet 1.2`
- 过滤条件：
  - `domain == singing`
  - `quality_flag == ok`
  - `gender in {male, female}`
  - `duration_sec` 在 `2` 到 `20` 秒之间
- 只保留相对中性的 technique：
  - `fast_forte`
  - `fast_piano`
  - `forte`
  - `pp`
  - `slow_forte`
  - `slow_piano`
  - `straight`
  - `vibrato`
- 明确排除：
  - `lip_trill`
  - `vocal_fry`
  - `inhaled`
  - `trillo`
  - 以及其他更强技巧性或不够中性的标签
- 平衡策略：
  - 按 `(gender, technique)` 划分 cell
  - 每个 technique 取男女两侧的最小样本数
  - cell 内按 `speaker_id` 做 round-robin

## 当前规模

- `clean_speech_v1`
  - 总计 `15100` 条
  - 女 `7550`
  - 男 `7550`
  - `VCTK` 女 `3775`
  - `VCTK` 男 `3775`
  - `LibriTTS-R` 女 `3775`
  - `LibriTTS-R` 男 `3775`

- `clean_singing_v1`
  - 总计 `2038` 条
  - 女 `1019`
  - 男 `1019`
  - technique 分布见 `clean_subset_summary_v1.csv`

## 设计取舍

- 这是“保守 clean subset”，不是“最大覆盖 subset”。
- `speech` 侧优先保证录音稳定、语言单一、男女和数据集平衡。
- `singing` 侧优先排掉技巧性过强的发声方式，避免它们主导谱差异。
- 当前版本还没有用全量自动声学特征做进一步筛选；后续可以在此基础上叠加响度、F0 成功率、静音比例等条件，形成 `v2`。

## 推荐用途

1. `clean_speech_v1` 作为阶段 0 的首个主分析集。
2. `clean_singing_v1` 作为阶段 0/1 的补充分析集。
3. 固定评测集继续使用 `experiments/fixed_eval/v1_2/`，不要和 clean subset 混用。
