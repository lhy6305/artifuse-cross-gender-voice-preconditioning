# 表示层路线：LPC 编辑与重建原型 v1

## 背景

在 `docs/36_representation_layer_pivot_v1.md` 完成表示层转型后，当前第一优先路线改为：

- 先选一个能较稳定承载 tract / resonance 信息的表示；
- 再验证该表示是否可以在尽量锁住 `f0` 与激励感的前提下被编辑；
- 最后才继续判断它是否值得进入后续更系统的主观与客观评估。

第一轮 probe 结果显示：

- `WORLD envelope` 分离度整体偏弱，只适合保留为对照；
- `LPC envelope` 在 `LibriTTS-R` 上分离度最强；
- `MFCC / cepstral proxy` 更均衡，但当前先作为第二候选。

因此当前先落地 `LPC / LSF` 路线的第一版编辑原型。

## 原型目标

`v1` 不是完整的 `LSF` 参数化编辑器，而是一个更保守的 `LPC residual-preserving pole edit probe`：

- 逐帧做 `LPC` 分析；
- 仅在 voiced 帧上操作；
- 对正频共轭极点里落在 `F1 / F2 / F3` 代理搜索带内的候选做角频率平移；
- 尽量保留原始 residual / excitation；
- 用 overlap-add 回到时域，先验证“是否比 envelope 更像改 tract / resonance，而不是改整体 pitch 感”。

## 实现落点

- 构建脚本：`scripts/build_stage0_speech_lpc_listening_pack.py`
- GUI 入口：`scripts/open_stage0_speech_lpc_review_gui.ps1`
- 配置：`experiments/stage0_baseline/v1_full/speech_lpc_resonance_candidate_v1.json`
- 正式听审包：`artifacts/listening_review/stage0_speech_lpc_listening_pack/v1/`

## 当前实现口径

- `male -> feminine`：上移前三个正频极点代理峰；
- `female -> masculine`：下移前三个正频极点代理峰；
- `LibriTTS-R` 与 `VCTK` 分别给独立搜索带和 `shift_ratio`；
- 通过 `blend` 限制编辑强度，避免直接滑向明显重合成感。

## 当前机器侧先验

`v1` 的自动量化摘要位于：

- `artifacts/listening_review/stage0_speech_lpc_listening_pack/v1/listening_review_quant_summary.md`

当前只把它当作弱先验：

- `avg auto_quant_score ≈ 70.51`
- `strong_pass = 2`
- `pass = 2`
- `fail = 4`

风险点也很清楚：

- `feminine` 侧响应更强；
- `masculine` 侧方向不稳，且多次出现 `wrong_direction / direction_weak`；
- 多行触发了 `rms_drift_gt_1p5db`，说明当前重建增益还不够稳。

## 当前结论

这版 `LPC v1` 已经完成“可运行、可导出、可听审”的第一目标，但还不能把自动量化当作有效性证明。

补充：

- 首次导出的 `v1` 包曾暴露一个重建增益错误：
  - overlap-add 窗函数归一化写法不对；
  - 少量尖峰触发了全局 peak limit，导致整段处理音被异常压低；
  - 该问题已修复，并已在原路径上重导 `stage0_speech_lpc_listening_pack/v1/`。
- 修复后已完成一轮正式听审：
  - `8/8 reviewed`
  - `effect_audible: maybe=4, no=4`
  - `strength_fit: too_weak=8`
  - 主观结论是“整体极弱、接近不可感知”，当前还没有证据表明它已跨过可用阈值。
- 听审 GUI 也顺手补了三项能力：
  - 播放时“增强响度并限峰值”，避免弱音频时 200% 音量几乎无效；
  - 左侧列表空白点击不再误选最后一条；
  - 新增“处理音(F0 对齐原音)”试听按钮，用于排除音调偏移带来的误判。

当前应优先做的不是继续堆参数，而是先听：

- 它是否终于比 `envelope v5` 更像在改共鸣腔体；
- 它是否在 `female -> masculine` 侧仍然会出现方向错误；
- 它是否把强度主要换成了新的重建伪影或 loudness 漂移。

## 下一步

1. 若继续保留 `LPC` 路线，下一轮必须显式提高强度，而不是沿当前 `v1` 原参数重复听审。
2. 下一轮听审默认应结合“处理音(F0 对齐原音)”按钮，先排除音调偏移影响。
3. 若加强后仍然基本不可感知，则需要尽快切到 `cepstral envelope` 对照线，而不是继续在当前 pole-edit 上硬推。
