# 表示层路线：Conditional Envelope Transport 原型 v2

## 背景

`conditional_envelope_transport v1` 已完成正式听审，结论非常明确：

- `8/8 reviewed`
- `effect_audible: no=8`

因此当前不能再把问题理解成“也许自动量化误杀了”。`v1` 的问题不是伪影过多，也不是方向明显反了，而是**整体直接不可分辨**。

## 为什么不直接放弃这条线

`v1` 的实现其实偏保守：

- 每帧只向目标参考包络做 `target pull`
- 仍有 `nearest_k=3` 的平均化
- 平滑和限幅也偏重

这更像“温和往目标侧靠一点”，而不是显式提取局部性别方向 delta。

所以 `v2` 不只是把系数拧大，而是把映射语义换掉：

- 不再用 `target_full - current_full`
- 改成 `target_anchor - source_anchor`

也就是：

1. 先在源性别参考库里找与当前帧内容最接近的 `source anchor`
2. 再在目标性别参考库里找对应的 `target anchor`
3. 用两者差分作为局部条件化方向 delta
4. 再把这个 delta 加回当前帧

## v2 的实现口径

脚本：

- `scripts/build_stage0_speech_conditional_envelope_transport_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_conditional_envelope_transport_candidate_v2.json`

相对 `v1` 的关键变化：

1. `delta_mode` 从隐含的 `target pull` 升级为 `contrastive_anchor`
2. `nearest_k` 从 `3` 收紧到 `1`，减少平均化抵消
3. `proxy_coeffs` 提高，增强内容对齐约束
4. `transport_ratio / blend / max_frame_delta_l2 / max_envelope_gain_db` 明显上调
5. 时间平滑收窄，避免把局部可辨变化继续抹平

因此 `v2` 回答的问题是：

**如果把每帧编辑从“往目标参考靠拢”升级成“显式注入目标-源局部对比 delta”，这条条件化路线能否 finally 跨过不可辨阈值。**

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v2/`
- GUI 入口：`scripts/open_stage0_speech_conditional_envelope_transport_review_gui.ps1 -PackVersion v2`

## 当前机器侧先验

量化摘要：

- `artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v2/listening_review_quant_summary.md`

当前机器侧先验相比 `v1` 略有提升，但仍然偏弱：

- `avg auto_quant_score ≈ 35.64`
- `avg auto_direction_score ≈ 7.18`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 9.63`
- `fail = 8/8`

也就是说：

- `v2` 比 `v1` 确实更强了一些；
- 但自动量化仍认为它整体处在“弱改动”区间；
- 因此这轮仍需要正式听审来判断它是不是再次被机器低估。

## 听审重点

这轮主观重点是：

1. 是否终于从 `8/8 no audible` 跨到至少“局部可辨”；
2. 若开始可辨，听感是不是 tract / resonance 改变，而不是整体亮暗或尖闷变化；
3. 是否因为取消平均化和加大 delta，重新引入伪影；
4. `masculine` 与 `feminine` 两侧是否有一边明显先起来。

## 当前状态

`conditional_envelope_transport v2` 随后已完成正式听审，当前主观结果是：

- `8/8 reviewed`
- `effect_audible: no=8`

因此当前结论非常明确：

- `v1` 不可辨识
- `v2` 换成更强的局部对比 delta 后仍然不可辨识
- 这说明问题不只是 `v1` 太保守，而是当前 `reference envelope transport` 家族本身没有给出足够正证据

因此这条线当前应正式收口，不再继续出常规 `v3`。
