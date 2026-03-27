# 表示层路线：Neural Envelope Latent 原型 v1

## 背景

到当前为止，以下三类路线都已经给出足够负证据：

- 经典手工 warp：`LSF / VTL`
- reference-based 包络搬运：`conditional_envelope_transport v1 / v2`
- linear low-rank latent：`low-rank envelope subspace v1`

其中 `low-rank v1` 的机器侧先验虽然比 `conditional transport` 更强，但正式听审仍然是 `8/8 no audible`。因此下一步不再继续围绕线性子空间和静态 affine latent 映射做小修小补，而是把表示层继续升级到**nonlinear / neural envelope latent**。

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_neural_envelope_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_neural_envelope_candidate_v1.json`

当前做法：

1. 从 `clean_speech_v1` 参考集按 `dataset` 聚合 voiced 段低阶倒谱包络帧；
2. 对每个数据集训练一个小型自编码器：
   - encoder：`cepstral envelope -> latent`
   - decoder：`latent -> cepstral envelope`
3. 在 latent 里分别统计 `female / male` 的 centroid 和 std；
4. 对待处理音频的每个 voiced 帧，先编码到 latent；
5. 再施加一个 `source_gender -> target_gender` 的 latent 映射；
6. 用 `decoder(target_latent) - decoder(current_latent)` 的差分回投包络空间，而不是直接用线性 basis 回投。

因此 `v1` 回答的问题是：

**如果把表示从 linear subspace 升级到 nonlinear autoencoder latent，这条线能否 finally 跨过“整体不可辨识”的门槛。**

## 与 low-rank 的区别

- `low-rank subspace`：`SVD basis + linear affine latent`
- `neural latent`：`autoencoder manifold + decoder difference`

这条线的目标不是简单加大线性位移，而是：

- 让 latent 本身承载更强的非线性结构；
- 让包络回投不再受限于单一线性 basis；
- 观察 nonlinear decoder 是否能把同样的 latent 位移翻译成更容易听见的结构变化。

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_neural_envelope_listening_pack/v1/`
- GUI 入口：`scripts/open_stage0_speech_neural_envelope_review_gui.ps1 -PackVersion v1`

## 当前状态

`neural envelope latent v1` 当前已完成：

- 正式包导出
- 量化队列与摘要生成
- `.\scripts\open_stage0_speech_neural_envelope_review_gui.ps1 -PackVersion v1 -AutoCloseMs 1200` smoke

当前机器侧先验：

- `avg auto_quant_score ≈ 49.44`
- `avg auto_direction_score ≈ 27.06`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 29.05`
- `borderline = 2`
- `fail = 6`

这说明：

- 当前 nonlinear latent `v1` 已经真正落地，不再只是线性 low-rank 的换皮；
- 但机器侧先验并没有自动优于 `low-rank v1`，甚至整体略弱；
- 因此这条线当前不能因为“是 neural”就默认更优，仍需要正式听审来确认机器侧是否再次误杀。

`neural envelope latent v1` 随后已完成正式听审，当前主观结果是：

- `8/8 reviewed`
- `effect_audible: no=8`

因此当前结论同样明确：

- 这条线不是“已有可辨变化但机器侧没看出来”；
- 而是和 `reference transport`、`linear low-rank latent` 一样，最终主观上仍然不可辨识；
- 这说明问题不只在线性子空间，当前这种**小型自编码器 + 静态 latent 映射** 也还没有跨过可辨阈值。

因此这条线当前应收口为 `null_result`，不继续沿 `neural envelope latent v2` 做常规小调参。

## 听审重点

这轮主观重点是：

1. 是否终于摆脱 `8/8 no audible`；
2. 若开始可辨，听感是否比 linear low-rank 更像结构性 tract / resonance 改变；
3. 是否会因为 nonlinear decoder 重新引入“假高频 / 变闷 / 不自然”；
4. 如果这版仍然不可辨，是否应继续升级到更强的 conditioned latent predictor / learned decoder，而不是继续做常规 `v2` 小调参。
