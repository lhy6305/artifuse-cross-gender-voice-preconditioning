# 表示层路线：Conditional Envelope Transport 原型 v1

## 背景

`LSF` 与 `VTL` 两条经典 warp 线都已完成正式听审，但都没有形成足够正证据：

- `LSF v1`：整体偏弱，且部分样本已有伪影；
- `VTL v1 / v2`：可辨性上来了，但仍偏弱，且轻微伪影频率偏高。

因此当前不再继续抠经典 `warp_ratio / smooth / band / energy rebalance`，而是升级到更高层但仍可解释的表示：

- 不做固定全局几何 warp；
- 不退回 `WORLD full resynthesis`；
- 保留原始相位；
- 把“编辑对象”从固定参数化，改成条件化参考包络搬运。

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_conditional_envelope_transport_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_conditional_envelope_transport_candidate_v1.json`

当前做法：

1. 从 `clean_speech_v1` 参考集按 `dataset x gender` 取一组干净参考语音；
2. 对参考语音提取 voiced 帧的低阶倒谱包络；
3. 按 `dataset x target_gender x f0桶` 建目标参考库；
4. 对待处理语音的每个 voiced 帧，取当前低阶倒谱前几维作为 `content proxy`；
5. 在对应目标库里做最近邻检索，取最近的目标包络向量；
6. 把当前帧包络向目标包络做受控平移，再做时间平滑；
7. 重建时保留原始相位，只动平滑谱包络层。

因此 `v1` 回答的问题是：

**如果不再施加固定全局 warp，而是按 `content + f0` 条件检索目标侧参考包络，是否能比 `LSF / VTL` 更稳定地给出方向正确且伪影更低的 tract / resonance 变化。**

## 与经典 warp 的区别

- `LSF / VTL`：先假设一个统一几何变形，再把所有内容都往同一个方向推；
- `conditional transport`：每个 voiced 帧先看自己更像什么内容，再去目标参考库里取“同类但目标侧”的包络。

因此它不是黑盒 wave-to-wave，而是：

- 仍保留解释性；
- 但允许不同内容、不同 `f0` 区间落到不同目标包络；
- 目标是避免“全局方向看着对，但只在局部低 `f0` 才成立”或者“整体可辨但像伪影”这类失败方式。

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v1/`
- GUI 入口：`scripts/open_stage0_speech_conditional_envelope_transport_review_gui.ps1 -PackVersion v1`

## 听审重点

这轮主观重点不是只看“有没有变化”，而是更具体地看：

1. 是否比 `VTL v2` 更少出现轻微双声感 / 伪影；
2. 是否不再只在局部低 `f0` 段才可辨；
3. `female -> masculine` 与 `male -> feminine` 两侧是否都更像 tract / resonance 改变，而不是整体亮暗拉伸；
4. 自动量化若仍给负面结论，是否再次出现“机器误杀”。

## 当前机器侧先验

量化摘要：

- `artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v1/listening_review_quant_summary.md`

当前机器侧先验明显偏弱：

- `avg auto_quant_score ≈ 31.76`
- `avg auto_direction_score ≈ 1.43`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 4.44`
- `fail = 8/8`

也就是说，这版至少在自动量化上表现成：

- 保真没有明显问题；
- 但改变量极弱；
- `direction` 也没有形成清晰正证据。

## 当前状态

`conditional_envelope_transport v1` 当前已完成：

- checkpoint 文档；
- 构建脚本；
- 配置；
- 正式听审包导出；
- 量化队列与摘要；
- GUI 入口 smoke。

当前入口：

- `scripts/open_stage0_speech_conditional_envelope_transport_review_gui.ps1 -PackVersion v1`

随后已完成正式听审，当前主观结果是：

- `8/8 reviewed`
- `effect_audible: no=8`

这轮结论没有歧义：

- 不是“可辨但方向不稳”
- 也不是“可辨但伪影太多”
- 而是整体直接不可分辨

因此这版应视为当前条件化路线的 `null result`。

因此下一步非常明确：

1. 不继续保留 `v1` 的 `target pull` 语义；
2. 直接改成更强的 `source-anchor -> target-anchor` 局部对比 delta；
3. 以 `v2` 继续验证这条条件化路线是否还能被救活。
