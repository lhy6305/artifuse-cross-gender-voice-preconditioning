# Stage 0 Full Report v1

## 数据健康

- clean_speech：`15100/15100` feature OK
- clean_singing：`2038/2038` feature OK
- fixed_eval_v1_2：`usable_yes=96;reviewed=96`

## 图表入口

- `plots/01_speech_feature_deltas.png`
- `plots/02_singing_centroid_delta_by_style.png`
- `plots/03_stable_bucket_tilt_deltas_speech.png`
- `plots/04_stable_bucket_tilt_deltas_singing.png`

## 关键观察

- `speech` 侧 `spectral_centroid_hz_mean` 在两个数据集上方向一致，说明 `pilot` 里的方向性在全量样本上被确认。
- `singing` 侧 style 效应仍然很强，不同 style 不能被直接折叠成一套规则。
- 稳健分桶改为按 dataset/style 自适应选 `quartile / tertile / median_split`，目标是最大化可比较 bin 数，而不是固定保留 4 桶。

## speech 侧 top delta

- `LibriTTS-R` | `spectral_centroid_hz_mean` | female_minus_male=`243.612757`
- `VCTK Corpus 0.92` | `spectral_centroid_hz_mean` | female_minus_male=`209.114640`

## singing 侧 spectral centroid delta

- `fast_forte` | female_minus_male=`1078.558173`
- `fast_piano` | female_minus_male=`973.353315`
- `pp` | female_minus_male=`869.917541`
- `slow_forte` | female_minus_male=`672.521876`
- `forte` | female_minus_male=`650.285934`
- `straight` | female_minus_male=`640.753773`
- `vibrato` | female_minus_male=`584.069162`
- `slow_piano` | female_minus_male=`569.357326`

## 稳健分桶选择

- `clean_speech` / `LibriTTS-R` -> `tertile` (bins=`3`, comparable=`3`, sparse=`0`, thresholds=`129.953/190.239`)
- `clean_speech` / `VCTK Corpus 0.92` -> `median_split` (bins=`2`, comparable=`2`, sparse=`0`, thresholds=`158.042`)
- `clean_singing` / `fast_forte` -> `median_split` (bins=`2`, comparable=`2`, sparse=`0`, thresholds=`273.055`)
- `clean_singing` / `fast_piano` -> `median_split` (bins=`2`, comparable=`2`, sparse=`0`, thresholds=`285.050`)
- `clean_singing` / `forte` -> `tertile` (bins=`3`, comparable=`1`, sparse=`2`, thresholds=`262.615/511.596`)
- `clean_singing` / `pp` -> `tertile` (bins=`3`, comparable=`1`, sparse=`2`, thresholds=`264.745/524.296`)
- `clean_singing` / `slow_forte` -> `median_split` (bins=`2`, comparable=`2`, sparse=`0`, thresholds=`326.899`)
- `clean_singing` / `slow_piano` -> `median_split` (bins=`2`, comparable=`2`, sparse=`0`, thresholds=`330.570`)
- `clean_singing` / `straight` -> `median_split` (bins=`2`, comparable=`2`, sparse=`0`, thresholds=`327.359`)
- `clean_singing` / `vibrato` -> `median_split` (bins=`2`, comparable=`2`, sparse=`0`, thresholds=`321.534`)

## 稀疏或低重叠提醒

- `clean_singing` / `forte` 仍有不可完全对齐的 bin；当前选择为 `tertile`。
- `clean_singing` / `pp` 仍有不可完全对齐的 bin；当前选择为 `tertile`。

## 输出文件

- `f0_bucket_summary_stable_v1.csv`
- `stage0_full_report_v1.md`
- `plots/`
