# 表示层路线：Conditioned Neural Envelope Predictor 原型 v1

## 背景

到当前为止，以下路线都已经给出足够负证据：

- 经典手工 warp：`LSF / VTL`
- reference-based 包络搬运：`conditional_envelope_transport v1 / v2`
- linear low-rank latent：`low-rank envelope subspace v1`
- static neural latent mapping：`neural envelope latent v1`

其中 `neural v1` 虽然已经升级到 nonlinear autoencoder latent，但主观仍然 `8/8 no audible`。因此下一步不再继续做静态 latent centroid/std 映射，而是继续升级到**conditioned latent predictor / learned decoder**。

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_conditioned_neural_envelope_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_conditioned_neural_envelope_candidate_v1.json`

当前做法：

1. 先按 `dataset` 训练小型自编码器，学习 `cepstral envelope -> latent -> envelope`；
2. 再按 `source_gender -> target_gender` 构造伪配对：
   - 以低阶倒谱 proxy 做跨性别最近邻内容匹配；
   - 得到 `source latent -> matched target latent` 的训练对；
3. 训练一个内容相关的 `latent translator`，而不是只做全局 centroid/std 平移；
4. 推理时先编码当前帧 latent，再由 translator 预测目标 latent；
5. 最后用 `decoder(predicted_target_latent) - decoder(current_latent)` 的差分回投包络空间。

因此 `v1` 回答的问题是：

**如果把 static latent mapping 升级到 conditioned latent predictor，这条线能否 finally 跨过“整体不可辨识”的门槛。**

## 与 neural v1 的区别

- `neural v1`：`static latent centroid/std mapping`
- `conditioned neural v1`：`content-aware latent translator + learned decoder`

这条线的目标是：

- 不再把所有样本都朝同一个全局 latent 方向推；
- 改成让映射显式依赖当前帧内容；
- 观察“条件化 predictor”是否比静态映射更容易产生可辨的结构变化。

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_conditioned_neural_envelope_listening_pack/v1/`
- GUI 入口：`scripts/open_stage0_speech_conditioned_neural_envelope_review_gui.ps1 -PackVersion v1`

## 当前状态

`conditioned neural envelope v1` 当前已完成：

- 正式包导出
- 量化队列与摘要生成
- `.\scripts\open_stage0_speech_conditioned_neural_envelope_review_gui.ps1 -PackVersion v1 -AutoCloseMs 1200` smoke

当前机器侧先验：

- `avg auto_quant_score ≈ 38.48`
- `avg auto_direction_score ≈ 11.45`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 13.29`
- `fail = 8`

这说明：

- 这条 conditioned predictor 主线已经真正落地；
- 但机器侧先验比 `neural v1` 还弱；
- 因此这轮既不能默认它更优，也不能只凭自动量化提前否掉，仍需要正式听审来确认机器侧是否再次误杀。

`conditioned neural envelope v1` 随后已完成正式听审，当前主观结果是：

- `8/8 reviewed`
- `effect_audible: no=8`

因此当前结论也已经足够明确：

- 这条线不是“content-aware predictor 已经开始起效，只是机器侧没看出来”；
- 而是和 `reference transport / low-rank / static neural latent` 一样，最终主观上仍然不可辨识；
- 这说明当前“包络表示学习 + 还原友好约束”的整条 mapping 家族，到这里已经给出成片负证据。

因此这条线当前应收口为 `null_result`，不继续沿 `conditioned neural v2` 做常规小调参。

## 听审重点

这轮主观重点是：

1. 是否终于摆脱 `8/8 no audible`；
2. 若开始可辨，听感是否比 static neural latent 更像结构性共鸣变化；
3. 是否会因为 conditioned translator 引入新的假高频、变闷或不自然；
4. 如果这版仍然不可辨，是否应进一步升级到更强的 predictor / decoder 架构，而不是继续出常规 `v2` 小调参。
