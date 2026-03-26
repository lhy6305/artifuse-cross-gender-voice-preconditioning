# Stage 0 候选信号短名单 v1

## 目标

这份短名单不是在直接写最终修正规则，而是在回答：

1. 哪些信号可以进入第一版候选先验。
2. 哪些信号只适合作为条件变量，不应该被直接修。
3. 哪些信号更适合作为分析监控或清洗参考。

当前判断基于：

- `experiments/stage0_baseline/v1_full/gender_feature_summary.csv`
- `experiments/stage0_baseline/v1_full/f0_bucket_summary_stable_v1.csv`
- `experiments/stage0_baseline/v1_full/f0_bucket_group_scheme_summary_v1.csv`
- `experiments/stage0_baseline/v1_full/stage0_full_report_v1.md`

## 一、可进入第一版候选先验的信号

### 1. `spectral_centroid_hz_mean`

保留理由：

- `speech` 侧方向一致：
  - `LibriTTS-R`：`+243.61 Hz`
  - `VCTK Corpus 0.92`：`+209.11 Hz`
- `singing` 侧在主要 style 上也稳定为正：
  - `fast_forte`：`+1078.56 Hz`
  - `fast_piano`：`+973.35 Hz`
  - `slow_forte`：`+672.52 Hz`
  - `straight`：`+640.75 Hz`
  - `vibrato`：`+584.07 Hz`

保留方式：

- 不直接用绝对均值差做修正规则。
- 第一版只把它当成“亮度 / 谱重心方向候选”，优先保留方向和相对强弱，不保留跨数据集绝对量级。
- `speech` 和 `singing` 必须分域处理。

### 2. `mean_log_centroid_minus_log_f0`

这是当前最接近“控制音高后仍残留的谱位置差异”的信号，优先级应高于裸 `spectral_centroid_hz_mean`。

当前稳健分桶中，值得优先关注的可比较 cell：

- `speech`
  - `LibriTTS-R` `low_band`：`+0.022`
  - `LibriTTS-R` `high_band`：`+0.015`
  - `VCTK Corpus 0.92` 两个可比较 bin 为负：`-0.127`、`-0.043`
- `singing`
  - `slow_forte high_band`：`+0.172`
  - `straight high_band`：`+0.169`
  - `fast_forte high_band`：`+0.168`
  - `vibrato high_band`：`+0.163`
  - `slow_piano high_band`：`+0.110`

当前解释：

- 这个信号已经足以作为第一版候选先验的主观察量。
- `speech` 侧不同数据集仍有方向分歧，因此暂时更适合作为“候选规则筛选指标”，而不是直接写成统一规则表。
- `singing` 侧高音区正向差异最稳定，优先级高于低音区。

## 二、应保留为条件变量，但不直接作为修正目标的信号

### 1. `f0_median_hz`
### 2. `f0_p10_hz`
### 3. `f0_p90_hz`

理由：

- 它们稳定地反映性别相关音高差异。
- 本项目的前置模块不应把“改音高”当主职责。
- 这些字段当前最重要的用途是：
  - 分桶
  - 条件控制
  - 强度上限切换

结论：

- 它们应进入规则系统的条件侧。
- 不应直接成为第一版 correction target。

## 三、目前只适合作为分析监控 / 清洗参考的信号

### 1. `rms_dbfs`

当前差异很大，但更像录音或演唱力度条件：

- `speech`
  - `LibriTTS-R`：`+0.98 dB`
  - `VCTK`：`-0.05 dB`
- `singing`
  - 多数 style 在 `+2.4 dB` 到 `+7.9 dB` 之间

结论：

- 可用于质量监控、style 差异解释、异常排查。
- 不建议直接写入第一版修正规则。

### 2. `silence_ratio_40db`

理由：

- 强依赖切分、留白、呼吸和句法结构。
- 更像结构性边界差异，而不是稳定的共鸣目标。

### 3. `f0_voiced_ratio`

理由：

- 受切分、延音、停顿和 VAD 边界影响大。
- 适合继续做分组解释或质量监控，不适合当成第一版修正规则。

## 四、当前不建议直接展开规则的 style

### 1. `forte`
### 2. `pp`

在稳健分桶里，这两个 style 当前都只保留一个中间可比较 bin：

- `forte`：`tertile`，`comparable=1`，`sparse=2`
- `pp`：`tertile`，`comparable=1`，`sparse=2`

当前事实是：

- 低区和高区几乎呈现男女分布分离。
- 中间窄重叠区才存在可比较样本。

结论：

- 第一版规则不应把这两个 style 当成“完整双边可对齐”的常规 style。
- 更合理的做法是先把它们标成“重叠受限 style”，只在中间可比较区做保守观察。

## 五、第一版候选规则的实际收缩方式

如果现在就要收缩成第一版候选规则，我建议只保留：

1. `speech`
   - 只保留 `spectral_centroid_hz_mean` 与 `mean_log_centroid_minus_log_f0` 的方向性观察
   - 先不写绝对增益表
2. `singing`
   - 优先保留 `fast_forte`
   - 优先保留 `fast_piano`
   - 优先保留 `slow_forte`
   - 优先保留 `slow_piano`
   - 优先保留 `straight`
   - 优先保留 `vibrato`
3. `forte` / `pp`
   - 只保留“中间重叠区可比较”的备注，不纳入第一版常规先验

## 六、下一步

当前最合理的下一步是：

1. 把候选先验限制在 `spectral centroid` 与 `log_centroid_minus_log_f0` 两条主线。
2. 为 `speech` 和 `singing` 分别写出第一版“方向性规则草案”。
3. 对 `singing` 的高音区与低音区分别做保守强度上限建议。

## 最后一句

当前阶段最重要的不是“把全部差异都变成规则”，而是：

- 先挑出少数真正可能有用的信号；
- 再把明显是录音、切分或 style 偏差的指标排除掉；
- 最后只对高置信度信号写第一版候选先验。
