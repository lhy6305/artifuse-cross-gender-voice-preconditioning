# Stage0 Speech Listening Pack v1

## 目标

在 `singing` 两轮都“人耳完全无感”之后，先不要继续微调同一套 singing 静态 EQ，而是切到更容易被人耳判断的 `speech-first`。

这一版的目的不是直接声明“规则已经成立”，而是先回答两个更基础的问题：

1. 静态 6 段 band-gain 在 `speech` 上到底能不能被听见。
2. 如果能被听见，它在不同数据集上是不是朝同一个方向工作。

## 输入池

输入来自：

- `experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv`

筛选条件：

- `domain == speech`
- `review_status == reviewed`
- `usable_for_fixed_eval == yes`
- `speaker_or_gender_bucket_ok == yes`

当前可用池规模：

- `LibriTTS-R / female = 11`
- `LibriTTS-R / male = 12`
- `VCTK Corpus 0.92 / female = 12`
- `VCTK Corpus 0.92 / male = 12`

## 选样策略

当前不追求“大样本覆盖”，而是先做低成本、平衡、容易反复重建的试听包。

构成方式：

- 按 `dataset_name x source_gender` 分成 4 个 cell
- 每个 cell 默认取 `2` 条样本
- 共 `8` 条

选样分数按以下几项离该 cell 中位数的距离组成：

- `duration_sec`
- `f0_median_hz`
- `spectral_centroid_hz_mean`

同时加轻微惩罚项：

- `silence_ratio_40db`
- `triage_score`

所以当前拿到的是“各 cell 内更居中、更像代表样本”的一小批 speech。

## 规则配置

当前使用独立的 speech 诊断配置：

- `experiments/stage0_baseline/v1_full/speech_rule_candidate_v1.json`
- `experiments/stage0_baseline/v1_full/speech_rule_band_gain_profiles_v1.json`

注意：

- 这不是正式 `v1` 规则表
- 这是 `speech-first audibility diagnostic`
- 目标是验证“是否可感知”和“方向是否稳定”，不是直接宣称 correction rule 已收敛

源性别到目标方向的映射仍然保持：

- `male -> feminine`
- `female -> masculine`

## 当前 profile 强度

相比 singing `v1 / v2`，这一版 speech profile 更激进。

大致范围：

- `LibriTTS-R feminine`: 主 boost 带到约 `+2.6 dB`
- `VCTK feminine`: 主 boost 带到约 `+2.0 dB`
- `LibriTTS-R masculine`: 主 cut 带到约 `-2.0 dB`
- `VCTK masculine`: 主 cut 带到约 `-1.8 dB`

原因很直接：

- 这轮首先要知道“静态 EQ 到底听不听得出来”
- 如果继续只给 `+0.3 dB / -0.2 dB` 量级，诊断价值太低

## 当前输出

临时产物位于：

- `tmp/stage0_speech_listening_pack/v1/`

其中包括：

- `original/`
- `processed/`
- `listening_pack_summary.csv`
- `listening_review_queue.csv`
- `listening_review_quant_summary.md`

这些都属于可重建临时文件，允许随时被清空。

## 首轮量化结果

当前 `8` 条 speech 样本的量化摘要：

- `avg auto_quant_score = 50.00`
- `avg auto_direction_score = 21.44`
- `avg auto_preservation_score = 98.52`
- `avg auto_effect_score = 43.19`
- `borderline = 2`
- `fail = 6`

更关键的是分布特征：

- `LibriTTS-R male -> feminine` 两条达到了 `borderline`
- `LibriTTS-R female -> masculine` 两条在当前代理口径下是 `wrong_direction`
- `VCTK female -> masculine` 两条也显示 `wrong_direction`
- `VCTK male -> feminine` 两条虽然改变量不小，但方向仍偏弱

## 当前解读

这轮结果和 singing 最大的不同是：

- 它不再是“全都弱到没信息”

现在已经能看到：

1. `speech` 上静态 band-gain 至少开始产生更明显的可量化改动
2. `LibriTTS-R` 与 `VCTK` 的响应并不一致
3. 当前 profile 更像“可感知性探针”，还不是“跨数据集稳定规则”

所以当前最合理的阶段结论是：

- `speech-first` 比 `singing` 更值得继续推进
- 但 `speech` 规则还不能直接冻结
- 下一轮应优先结合人工听审，判断：
  - `LibriTTS-R feminine` 是否真的开始可感知
  - `masculine` profile 是否只是代理口径不对，还是人耳上也不对
  - `VCTK` 是否需要单独 profile，而不应共用同一路线

## 启动命令

### 重建 speech 试听包

```powershell
.\python.exe .\scripts\build_stage0_speech_listening_pack.py
```

### 重建 speech 量化队列

```powershell
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --rule-config experiments/stage0_baseline/v1_full/speech_rule_candidate_v1.json `
  --summary-csv tmp/stage0_speech_listening_pack/v1/listening_pack_summary.csv `
  --output-csv tmp/stage0_speech_listening_pack/v1/listening_review_queue.csv `
  --summary-md tmp/stage0_speech_listening_pack/v1/listening_review_quant_summary.md
```

### 直接打开 speech 听审 GUI

PowerShell:

```powershell
.\scripts\open_stage0_speech_review_gui.ps1
```

`cmd.exe`:

```cmd
.\scripts\open_stage0_speech_review_gui.cmd
```

### GUI smoke

```powershell
.\scripts\open_stage0_speech_review_gui.ps1 -AutoCloseMs 2000
```
