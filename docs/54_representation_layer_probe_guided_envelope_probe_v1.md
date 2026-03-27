# 表示层路线：Probe-Guided Envelope Residual 原型 v1

## 背景

到当前为止，以下整条 envelope mapping 家族都已经给出负证据：

- `conditional transport v1 / v2`
- `low-rank envelope subspace v1`
- `neural envelope latent v1`
- `conditioned neural envelope v1`

它们的共同点是：都在试图“学习一个目标表示或目标映射”，然后保守地把当前帧往那个表示推过去。现在需要验证的，不再是“能否学到更好的 mapping”，而是：

**如果直接围绕目标判别方向做有约束的 envelope residual 优化，这条线能否 finally 跨过不可辨阈值。**

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_probe_guided_envelope_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_probe_guided_envelope_candidate_v1.json`

当前做法：

1. 从 `clean_speech_v1` 参考集按 `dataset` 提取 voiced 段低阶倒谱包络帧；
2. 为每个数据集训练一个小型 `gender probe`，直接判别 `female / male`；
3. 推理时对当前帧的归一化倒谱包络做小步优化：
   - 目标：让 `probe` 更偏向目标性别
   - 约束：`L2 / L1 / max_frame_delta_l2 / gain cap / time smooth`
4. 最终只把优化得到的包络残差回投到原始相位重建链路。

因此 `v1` 回答的问题是：

**如果不再学习 target mapping，而是直接优化“目标方向判别分数”，这条线能否 finally 跨过“整体不可辨识”的门槛。**

## 与前一条路线的区别

- `conditioned neural v1`：先学内容相关 translator，再预测目标 latent
- `probe-guided v1`：直接在当前帧附近做 bounded optimization，优化目标就是“更像目标方向”

这条线的目标是：

- 删掉“目标表示学习是否正确”这层不确定性；
- 直接测试 envelope-only 编辑在判别目标驱动下，是否终于能推到可辨；
- 如果这版仍然不可辨，就更有理由认为“当前 envelope-only 原始相位重建家族”本身已经接近穷尽。

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_probe_guided_envelope_listening_pack/v1/`
- GUI 入口：`scripts/open_stage0_speech_probe_guided_envelope_review_gui.ps1 -PackVersion v1`

## 当前状态

`probe-guided envelope v1` 当前已完成：

- 正式包导出
- 量化队列与摘要生成
- `.\scripts\open_stage0_speech_probe_guided_envelope_review_gui.ps1 -PackVersion v1 -AutoCloseMs 1200` smoke

当前机器侧先验：

- `avg auto_quant_score ≈ 41.62`
- `avg auto_direction_score ≈ 15.91`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 17.86`
- `fail = 8`

这说明：

- 这条 direct residual 主线已经真正落地；
- 机器侧先验仍然偏负，但比 `conditioned neural v1` 稍高；
- 因此当前下一步仍应做正式听审，而不是只看自动量化。

## 听审重点

这轮主观重点是：

1. 是否终于摆脱 `8/8 no audible`；
2. 若开始可辨，听感是否比 mapping 家族更像直接的性别方向推动；
3. 是否因为直接优化而引入新的尖锐、发空、脏声或不自然；
4. 如果这版仍然不可辨，是否应正式收缩到“envelope-only 原始相位重建家族整体 exhausted”的阶段判断。
