# Stage 0 Baseline Analysis

- 运行模式：`full`
- speech 输入条数：`15100`
- singing 输入条数：`2038`
- 固定评测集终稿：`usable_yes=96;reviewed=96`

## 输出文件

- `input_snapshot/clean_speech_input.csv`
- `input_snapshot/clean_singing_input.csv`
- `clean_speech_enriched.csv`
- `clean_singing_enriched.csv`
- `analysis_overview.csv`
- `gender_feature_summary.csv`
- `f0_bucket_summary.csv`

## 观察摘要

- clean_speech feature OK：`15100/15100`
- clean_singing feature OK：`2038/2038`

### speech 侧 spectral centroid 差异较大的 group

- dataset_name=LibriTTS-R，female_minus_male=243.612757
- dataset_name=VCTK Corpus 0.92，female_minus_male=209.114640

### singing 侧 spectral centroid 差异较大的 group

- coarse_style=fast_forte，female_minus_male=1078.558173
- coarse_style=fast_piano，female_minus_male=973.353315
- coarse_style=pp，female_minus_male=869.917541
- coarse_style=slow_forte，female_minus_male=672.521876

## 备注

- 本轮只固定第一版基线入口，不把统计显著性和热图一次做满。
- `f0_bucket_summary.csv` 使用当前样本的 `f0_median_hz` 四分位做分桶。
- 全量特征提取支持断点续跑，可分开先跑 speech 再跑 singing。
