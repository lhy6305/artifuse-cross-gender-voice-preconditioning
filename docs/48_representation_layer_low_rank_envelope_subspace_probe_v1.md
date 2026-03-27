# 表示层路线：Low-Rank Envelope Subspace 原型 v1

## 背景

到当前为止，以下两类路线都已经给出足够负证据：

- 经典手工 warp：`LSF / VTL`
- reference-based 包络搬运：`conditional_envelope_transport v1 / v2`

尤其是后者，已经连续两轮主观 `8/8 no audible`。因此下一步不再继续围绕逐帧参考包络做 retrieval / transport，而是把表示层升级到**学习型低维包络子空间**。

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_low_rank_envelope_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_low_rank_envelope_candidate_v1.json`

当前做法：

1. 从 `clean_speech_v1` 参考集按 `dataset` 聚合 voiced 段低阶倒谱包络帧；
2. 对每个数据集学习一个共享的低秩子空间：
   - 全体帧均值 `mean_vector`
   - 低秩基 `basis`
3. 在这个子空间里分别统计 `female / male` 的 latent centroid 和 latent std；
4. 对待处理音频的每个 voiced 帧，先投影到该 latent space；
5. 再施加一个 `source_gender -> target_gender` 的 latent affine 映射：
   - 均值向目标 centroid 平移
   - 方差按目标/源的比例做受控缩放
6. 把 latent delta 投回包络空间，只改平滑谱包络，重建仍保留原始相位。

因此 `v1` 回答的问题是：

**如果不再直接编辑逐帧 reference 向量，而是在 learned low-rank envelope latent 里做性别条件映射，这条线能否 finally 跨过“整体不可辨识”的门槛。**

## 与上一条路线的区别

- `conditional transport`：每帧去参考库里找目标包络；
- `low-rank subspace`：先学一个稳定的包络 latent，再在 latent 里做性别映射。

这条线的目标不是“更像哪条参考语音”，而是：

- 把编辑对象变成更稳定、更低维的 learned representation；
- 降低 reference 检索带来的稀释和平均化；
- 提高每次编辑的结构一致性。

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_low_rank_envelope_listening_pack/v1/`
- GUI 入口：`scripts/open_stage0_speech_low_rank_envelope_review_gui.ps1 -PackVersion v1`

## 当前状态

`low-rank envelope subspace v1` 当前已完成：

- 正式包导出
- 量化队列与摘要生成
- `.\scripts\open_stage0_speech_low_rank_envelope_review_gui.ps1 -PackVersion v1 -AutoCloseMs 1200` smoke

实现层补充：

- 已补一处子空间一致性修正：共享 latent 统计统一在学习时的完整 `keep_coeffs` 维度上完成；
- 对较保守规则只屏蔽高阶系数的回投改动，不再在推理时直接截断 `basis / centroid / std` 的统计语义。

当前机器侧先验：

- `avg auto_quant_score ≈ 52.72`
- `avg auto_direction_score ≈ 31.09`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 34.92`
- `borderline = 2`
- `fail = 6`

这说明：

- 它已明显强于 `conditional transport v1 / v2`；
- 但 `direction` 仍然偏弱，整体还没有进入机器侧正证据区间；
- 因此当前默认下一步不是继续在纸面上推 `v2`，而是先做 `v1` 的正式听审。

`low-rank envelope subspace v1` 随后已完成正式听审，当前主观结果是：

- `8/8 reviewed`
- `effect_audible: no=8`

因此当前结论也很明确：

- 这条线不是“略可辨但方向不足”；
- 而是和 `conditional transport v1 / v2` 一样，最终主观上仍然不可辨识；
- 这说明问题不只是 reference retrieval 太弱，当前这种**线性 low-rank latent affine** 编辑本身也还没有跨过可辨阈值。

因此这条线当前应收口为 `null_result`，不继续沿 `linear low-rank subspace v2` 常规加参。

## 听审重点

这轮主观重点是：

1. 是否终于摆脱 `8/8 no audible`；
2. 若开始可辨，听感是否比 `cepstral delta` 更像结构性 tract / resonance 变化；
3. 是否会重新掉回“假高频 / 变闷 / 伪影”；
4. `learned latent` 这条线是否值得继续升级到更强的 nonlinear / neural envelope 表示。
