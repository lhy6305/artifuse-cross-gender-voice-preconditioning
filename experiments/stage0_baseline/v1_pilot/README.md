# Stage 0 Baseline Analysis

- 运行模式：`pilot`
- speech 输入条数：`256`
- singing 输入条数：`256`
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

- clean_speech feature OK：`256/256`
- clean_singing feature OK：`256/256`

### speech 侧 spectral centroid 差异较大的 group

- dataset_name=LibriTTS-R，female_minus_male=239.887916
- dataset_name=VCTK Corpus 0.92，female_minus_male=17.005541

### singing 侧 spectral centroid 差异较大的 group

- coarse_style=straight，female_minus_male=1180.444184
- coarse_style=slow_piano，female_minus_male=634.497085
- coarse_style=fast_piano，female_minus_male=607.832148
- coarse_style=slow_forte，female_minus_male=497.048382

## 备注

- 本轮只固定第一版基线入口，不把统计显著性和热图一次做满。
- `f0_bucket_summary.csv` 使用当前样本的 `f0_median_hz` 四分位做分桶。
- 如需全量开跑，可去掉 `--pilot` 并保留同一输出结构。
