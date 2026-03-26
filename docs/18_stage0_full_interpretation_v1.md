# Stage 0 Full 结果解释 v1

## 这份文档回答什么

当前 `full` 已经不再是“链路是否能跑通”的问题，而是在回答：

1. 哪些 `pilot` 观察在全量样本上被确认。
2. 哪些差异更接近项目真正关心的目标信号。
3. 哪些差异仍然更像数据集、style 或分桶方式带来的偏差。
4. 下一步图表和候选修正规则应该怎么收缩范围。

当前对应原始输出位于：

- `experiments/stage0_baseline/v1_full/analysis_overview.csv`
- `experiments/stage0_baseline/v1_full/gender_feature_summary.csv`
- `experiments/stage0_baseline/v1_full/f0_bucket_summary.csv`
- `experiments/stage0_baseline/v1_full/README.md`

## 先给一句总判断

当前 `full` 结果说明：

- 阶段 0 的基础缓存已经稳定可用。
- `speech` 与 `singing` 都存在清晰的性别相关差异。
- `f0` 仍然必须作为条件变量，不能把谱差异和音高差异混着解释。
- `speech` 侧的“方向”比 `pilot` 更稳定了，但跨数据集的绝对分布差异依然很大。
- `singing` 侧的 style / technique 效应非常强，不能把不同 style 直接揉成一套规则。
- 当前已经可以进入“图表 + 候选信号筛选”阶段，但还不适合直接写最终修正规则。

## 一、先确认输出是否健康

`analysis_overview.csv` 显示：

- `clean_speech`：`15100` 条，女 `7550`，男 `7550`，特征提取成功 `15100/15100`
- `clean_singing`：`2038` 条，女 `1019`，男 `1019`，特征提取成功 `2038/2038`
- `fixed_eval_v1_2`：`96` 条，`usable_yes=96`，`reviewed=96`

这说明当前 `v1_full` 可以当作后续阶段 0 图表和解释的正式缓存入口。

## 二、哪些 `pilot` 观察在全量上被确认

### 1. `speech` 侧的音高差异稳定存在

在两个 `speech` 数据集里，`f0` 相关差异方向完全一致：

- `LibriTTS-R`
  - `f0_median_hz`：女 `197.07`，男 `128.03`，差 `69.04`
  - `f0_p90_hz`：女 `262.11`，男 `175.58`，差 `86.53`
- `VCTK Corpus 0.92`
  - `f0_median_hz`：女 `203.34`，男 `111.87`，差 `91.47`
  - `f0_p90_hz`：女 `247.49`，男 `141.98`，差 `105.52`

这和 `pilot` 一致，说明：

- 性别相关音高差异不是抽样噪声。
- 后续任何谱差异解释都必须显式控制 `f0`。

### 2. `speech` 侧 `spectral_centroid` 的方向在全量上变得一致

`pilot` 里最需要警惕的是 `speech` 侧跨数据集不一致；到了 `full`，方向已经稳定：

- `LibriTTS-R`：女 `2041.26`，男 `1797.65`，差 `243.61`
- `VCTK Corpus 0.92`：女 `4871.47`，男 `4662.35`，差 `209.11`

这说明：

- “女侧谱重心更高”在当前 `speech` clean subset 中不是偶然现象。
- 但绝对量级依然明显受数据集录音链路和切分风格影响，不能直接把跨数据集均值当成通用修正量。

### 3. `singing` 侧的 style 条件差异非常稳定

在全部主要 style 上，女减男的 `spectral_centroid_hz_mean` 都显著为正：

- `fast_forte`：`+1078.56`
- `fast_piano`：`+973.35`
- `pp`：`+869.92`
- `slow_forte`：`+672.52`
- `forte`：`+650.29`
- `straight`：`+640.75`
- `vibrato`：`+584.07`
- `slow_piano`：`+569.36`

同时，`f0_median_hz` 在全部 style 上也稳定显著为正：

- 最小约 `+162.79`（`vibrato`）
- 最大约 `+260.88`（`pp`）

这说明：

- `singing` 侧确实不是噪声主导。
- `style` 条件必须保留，不能简单折叠。

## 三、当前更像目标信号的部分

这里的“目标信号”指的是：更可能和“跨性别转换中的薄、空、腔体感不匹配”有关，而不是单纯的录音电平或切分副产物。

### 1. 控制 `f0` 之后仍保留的谱差异

`f0_bucket_summary.csv` 说明，差异不只是“女声音高更高”：

- `clean_speech` 的全局四分位阈值为 `117.19 / 162.05 / 198.68 Hz`
- `clean_singing` 的全局四分位阈值为 `180.09 / 319.22 / 373.81 Hz`

在这些桶内，`mean_log_centroid_minus_log_f0` 仍有系统性变化，说明：

- `spectral centroid` 相对 `f0` 的位置仍在变化。
- 这比单纯的 `f0` 差异更接近前置修正真正该碰的东西。

### 2. `speech` 与 `singing` 共同出现的方向

当前最值得继续盯的，不是单个数值最大的特征，而是跨域方向一致的特征：

- `spectral_centroid_hz_mean`
- `f0` 分桶后的 `mean_log_centroid_minus_log_f0`

原因是：

- 它们在 `speech` 与 `singing` 中都不是随机翻转。
- 它们比 `rms_dbfs`、`silence_ratio` 更接近谱包络和共鸣位置本体。

## 四、当前更像偏差源的部分

### 1. `speech` 侧仍然存在很强的跨数据集分布差异

虽然 `spectral_centroid` 的方向已经一致，但绝对分布差异仍非常大：

- `LibriTTS-R` 女均值约 `2041 Hz`
- `VCTK` 女均值约 `4871 Hz`

同样，`f0_voiced_ratio` 和 `rms_dbfs` 也显示出明显数据集风格差异：

- `LibriTTS-R` 女 `rms_dbfs=-17.68`
- `VCTK` 女 `rms_dbfs=-26.79`
- `LibriTTS-R` 女 `f0_voiced_ratio=0.8335`
- `VCTK` 女 `f0_voiced_ratio=0.4369`

这更像：

- 切分长度差异
- 停顿结构差异
- 录音与响度分布差异

因此当前不应把这些绝对均值直接写成修正规则。

### 2. `singing` 侧的电平和静音差异更像 style / 录音条件

例如：

- `fast_piano`：`rms_dbfs` 女减男 `+7.87 dB`
- `slow_piano`：`rms_dbfs` 女减男 `+7.94 dB`
- `fast_piano`：`silence_ratio_40db` 女减男 `+0.1220`

这些值很大，但更可能反映：

- 演唱力度
- 采样与录音电平
- 呼吸与句法结构
- 切分方式

它们可以用于：

- 清洗和异常提示
- 分桶和条件控制

但不适合作为第一版前置修正的直接目标。

## 五、当前分桶方案暴露出的新问题

`f0_bucket_summary.csv` 还暴露出一个必须处理的新问题：全局四分位分桶在边缘性别桶上过于稀疏。

例如：

- `clean_speech` 中 `female q1_low` 只有 `1` 到 `3` 条
- `clean_singing` 中有 `17` 个 cell 的 `num_rows < 10`

这说明当前按“全体样本四分位”切桶，会自然产生：

- `female low f0`
- `male high f0`

这些极少数桶，而这些桶的均值不适合拿来做稳定解释。

下一轮更合理的方向是：

1. 改成更稳健的条件分桶，例如重叠区间或更粗的固定阈值桶。
2. 对低样本桶加显式最小样本数门槛。
3. 在图表中把稀疏桶单独标出来，避免误读。

## 六、当前可以支持什么结论

当前 `full` 已经可以支持的结论有：

- 阶段 0 的 `full` 缓存已经可用，且提取成功率为 `100%`。
- `speech` 与 `singing` 中都存在稳定的性别相关差异。
- `f0` 必须作为条件变量。
- `speech` 侧的谱差异方向已经比 `pilot` 更稳定。
- `singing` 侧必须保留 style / technique 条件。
- `spectral_centroid` 与 `log_centroid_minus_log_f0` 是当前最值得继续看的候选信号。

当前还不能直接支持的结论有：

- 具体该修多少频带。
- `speech` 和 `singing` 是否能共享同一套修正表。
- 当前全局四分位 `f0` 分桶是否已经足够稳健。
- 统计上显著的差异是否一定对应主观听感收益。

## 七、下一步建议

当前最合理的推进顺序是：

1. 基于 `v1_full` 先补第一版图表和 markdown 报告。
2. 明确哪些图表只做“描述性观察”，哪些图表可作为候选规则筛选。
3. 把 `f0` 分桶改成更稳健的条件分桶方案，再复算一次桶级表。
4. 只从跨数据集/跨 style 方向稳定、且在控制 `f0` 后仍存在的信号里挑候选修正规则。

## 最后一句

`pilot` 证明了“问题可分析”，而当前 `full` 进一步证明了：

- 这个问题不是抽样噪声。
- 但它也不是一套全局静态均值差就能解释完的。

接下来真正该做的，是把 `full` 结果压缩成更稳健的图表与候选信号，而不是直接跳进最终规则或模型实现。
