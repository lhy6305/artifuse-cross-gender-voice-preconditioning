# 表示层路线：Cepstral Envelope 对照原型 v1

## 背景

在 `LPC pole edit v2` 被主观确认成“可辨识但方向与机理都不对”之后，当前主线不再继续沿极点代理峰平移硬推，而是切到更平滑、更整体的表示编辑：

- 不改 `f0`
- 不做显式极点搬移
- 保留原相位与大部分细节
- 只对低阶倒谱包络做条件化位移

这条线对应表示层 pivot 里原先的 `cepstral envelope / low-order cepstral proxy` 方向。

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_cepstral_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_cepstral_envelope_candidate_v1.json`

当前做法：

1. 从 `clean_speech_v1` 参考集按 `dataset_name x gender` 抽样；
2. 对每条参考语音提取 voiced 帧的低阶倒谱 centroid；
3. 对每个数据集构建 `female - male` 与 `male - female` 的 centroid 差分；
4. 在待处理音频上，只对 voiced 帧的低阶倒谱系数注入该差分；
5. 保留原始相位，并把改动限制在平滑谱包络层。

因此 `v1` 回答的问题是：

**如果直接在低阶倒谱包络上做 dataset-conditioned 性别方向差分，是否会比 LPC pole edit 更少出现“瓶中感 / 人造高频感”。**

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_cepstral_listening_pack/v1/`
- GUI 入口：`scripts/open_stage0_speech_cepstral_review_gui.ps1 -PackVersion v1`

## 当前机器侧先验

量化摘要：

- `artifacts/listening_review/stage0_speech_cepstral_listening_pack/v1/listening_review_quant_summary.md`

当前机器侧先验明显比 `LPC v2` 更整齐：

- `avg auto_quant_score ≈ 85.23`
- `avg auto_direction_score ≈ 77.87`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 80.74`
- `strong_pass = 6`
- `borderline = 2`
- `fail = 0`

同时本轮电平复核正常，未再出现异常低电平问题。

## 当前状态

`cepstral v1` 已完成：

- 构建脚本
- 配置
- 听审包导出
- 队列与量化摘要
- GUI 入口 smoke

随后已完成正式听审，当前主观结果是：

- `8/8 reviewed`
- `effect_audible: yes=1, maybe=4, no=3`
- `direction_correct: maybe=4`
- `artifact_issue: slight=3`
- `strength_fit: too_weak=4`

结合人工描述，这版的失效模式已经比较清楚：

- 整体影响轻微；
- 相对“改变腔体”，更像在添加伪影；
- `male -> feminine` 侧更明显，听感像刻意添加高频，甚至带一点噪声感；
- 因此主观上仍然怀疑方向不对。

也就是说，`cepstral v1` 虽然比 `LPC v2` 更平滑，但还没有跨到“更接近目标共鸣结构”的那一边。

## 下一步

1. 当前不再把 `cepstral v1` 视为可直接继续扩展的主线实现。
2. 这条线按听审汇总仍可记作 `watch_with_risk`，但工程判断应明确为：
   - 不升格
   - 当前实现停止继续硬推
3. 下一步应进一步升级表示层，而不是继续沿这版低阶倒谱差分加参数：
   - 显式 `LSF` 参数化
   - 或更强的 source-filter / neural envelope 表示
