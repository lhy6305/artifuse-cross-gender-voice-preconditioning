# 表示层路线：Joint Source-Filter Residual 原型 v1

## 背景

到当前为止，以下整条 `envelope-only` 原始相位重建家族都已经给出负证据：

- `conditional transport v1 / v2`
- `low-rank envelope subspace v1`
- `neural envelope latent v1`
- `conditioned neural envelope v1`
- `probe-guided envelope v1`

其中 `probe-guided v1` 已经把方法层级升级到了 discriminative objective，但正式听审仍然是 `8/8 no audible`。因此下一步不再继续在纯包络空间里加力，而是直接验证：

**如果把表示对象从 envelope-only 升级到 joint source-filter residual，这条线能否 finally 跨过不可辨阈值。**

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_source_filter_residual_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_source_filter_residual_candidate_v1.json`

当前做法：

1. 从 `clean_speech_v1` 参考集按 `dataset` 提取 voiced 帧；
2. 对每个 voiced 帧，不再只取低阶包络，而是联合构造：
   - `low-order cepstral envelope`
   - `voiced harmonic residual band proxy`
3. 为每个数据集训练一个小型 `gender probe`，直接判别 `female / male`；
4. 推理时对当前帧的 joint feature 做 bounded optimization：
   - 目标：让 `probe` 更偏向目标性别
   - 约束：`L2 / L1 / envelope gain cap / detail-band cap / time smooth`
5. 最终把 joint delta 回投到原始相位 `STFT magnitude`：
   - 低阶部分作为 envelope delta
   - residual band 部分作为 voiced harmonic residual gain mask

因此 `v1` 回答的问题是：

**如果不再只改 tract / envelope，而是显式把 source-side voiced residual proxy 一起拉进优化，这条线能否 finally 跨过“整体不可辨识”的门槛。**

## 与 probe-guided envelope v1 的区别

- `probe-guided envelope v1`：只优化低阶包络
- `source-filter residual v1`：联合优化 `envelope + voiced harmonic residual proxy`

这条线的目标是：

- 删掉“只改 filter 半边”的强约束；
- 在不回到 `WORLD full resynthesis` 的前提下，引入 source/filter 联合方向信息；
- 验证 envelope-only 的失败，是否主要因为少了 excitation / harmonic residual 这一半。

## 为什么不是回到 WORLD full resynthesis

这条线虽然升级到 `joint source-filter`，但实现仍然保留：

- 原始相位
- 原始时域细节
- 原始整体时长与主音高结构

原因很直接：

- 早先 `WORLD source-filter / vocal-tract morph v1` 的失败点在于重合成本身引入底噪和瞬态脏声；
- 当前要验证的是“联合表示是否更有效”，而不是重新把 `WORLD full resynthesis` 副作用带回来。

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_source_filter_residual_listening_pack/v1/`
- GUI 入口：`scripts/open_stage0_speech_source_filter_residual_review_gui.ps1 -PackVersion v1`

## 听审重点

这轮主观重点是：

1. 是否终于摆脱 `8/8 no audible`；
2. 若开始可辨，听感是否比 envelope-only 更像 joint source/filter 的结构变化；
3. 是否因为引入 residual band proxy 而出现新的尖锐、沙、脏或发空；
4. 如果这版仍然不可辨，是否应进一步收缩到“轻量 source-filter residual 也不足以支撑主观可辨”的阶段判断。
