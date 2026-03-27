# 表示层路线：VTL Warping 原型 v2

## 背景

`docs/42_representation_layer_vtl_warping_probe_v1.md` 已经把 `VTL v1` 的主观失效模式写清：

- 一部分样本只有局部低 `f0` 段才可辨
- `F0` 对齐试听版本常出现明显伪影
- 部分处理音有轻微双声叠加感

因此 `v2` 的目标不是简单加力，而是先处理这些具体失效模式。

## v2 的改动点

配置：

- `experiments/stage0_baseline/v1_full/speech_vtl_warping_candidate_v2.json`

相对 `v1` 的主要变化：

- `wet_mix: 0.88~0.90 -> 1.0`
  - 直接去掉 dry/wet 叠加，优先压低双声感
- `voiced_smooth_frames: 4 -> 6`
  - 提高时域连续性，减少只在局部低 `f0` 段突然冒出来的感觉
- `freq_smooth_bins: 9 -> 11`
  - 让 tract band 位移更平滑
- `active_until_hz / taper_end_hz` 适度上扩
  - 让 tract 作用覆盖更完整，但仍保留高频渐隐
- 新增 `energy_rebalance_ratio`
  - 不再做 `v1` 那种“100% 带内能量回平”
  - 改成部分回平，避免把方向量几乎全部抵消掉

脚本侧对应新增了：

- `energy_rebalance_ratio`

因此 `v2` 的意图是：

- 保留 `VTL` 的 tract-length warp 机理
- 但不再让 `dry/wet` 混合和过硬的能量回平主导失败模式

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v2/`
- 队列：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v2/listening_review_queue.csv`
- 量化摘要：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v2/listening_review_quant_summary.md`

## 当前机器侧先验

当前 `v2` 已完成：

- 正式包导出
- 量化队列生成
- `.\scripts\open_stage0_speech_vtl_review_gui.ps1 -PackVersion v2 -AutoCloseMs 1200` smoke

量化摘要如下：

- `avg auto_quant_score ≈ 39.26`
- `avg auto_direction_score ≈ 0.10`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 36.86`
- `fail = 8`

和 `v1` 相比，当前图景是：

- `effect_score` 确实上来了
- 但 `direction_score` 进一步恶化
- 自动量化当前把它视为“更可辨，但方向更不可信”

因此 `v2` 还远谈不上“机器侧转正”，但它至少已经把问题从 `dry/wet` 叠加推进到更聚焦的方向问题。

## 下一步

1. 当前默认下一轮正式听审对象切到 `VTL v2`：
   - `.\scripts\open_stage0_speech_vtl_review_gui.ps1 -PackVersion v2`
2. 听审时优先回答三件事：
   - 双声感是否明显下降
   - 低 `f0` 局部才可辨的问题是否缓解
   - 自动量化里的 `wrong_direction` 是否仍然被人耳确认
3. 如果主观上方向仍然普遍不对，下一步就不应继续在 `VTL warp ratio` 上硬推，而应重新定义方向映射本身。
