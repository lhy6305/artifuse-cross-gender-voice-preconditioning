# 表示层路线：LPC 编辑与重建原型 v2

## 背景

`docs/37_representation_layer_lpc_edit_probe_v1.md` 对应的 `LPC v1` 已完成听审，结论很明确：

- `8/8 reviewed`
- `effect_audible: maybe=4, no=4`
- `strength_fit: too_weak=8`

也就是说，`v1` 已经足够说明“这条表示层路线可以落到可运行原型”，但还不足以说明“当前参数已经跨过主观可辨识阈值”。

因此当前不再重复 `v1`，而是直接构建更强的 `LPC v2`。

## v2 的改动点

配置位于：

- `experiments/stage0_baseline/v1_full/speech_lpc_resonance_candidate_v2.json`

相对 `v1` 的主要变化：

- `lpc_order`：`16 -> 18`
- `blend`：整体提高到 `0.90 ~ 0.92`
- `F1 / F2 / F3` 代理搜索带略放宽
- `shift_ratio` 明显加大
  - feminine 侧：更强上移
  - masculine 侧：更强下移

目标不是直接证明它已可用，而是更干净地回答一个问题：

**LPC 路线到底只是 v1 太弱，还是即使加到更高强度也仍然打不中共鸣主观感知。**

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_lpc_listening_pack/v2/`
- GUI 入口：`scripts/open_stage0_speech_lpc_review_gui.ps1 -PackVersion v2`

## 当前机器侧先验

量化摘要位于：

- `artifacts/listening_review/stage0_speech_lpc_listening_pack/v2/listening_review_quant_summary.md`

当前信号比 `v1` 更强：

- `avg auto_quant_score ≈ 80.19`
- `avg auto_direction_score ≈ 70.49`
- `avg auto_preservation_score ≈ 98.61`
- `avg auto_effect_score ≈ 75.54`
- `strong_pass = 5`
- `borderline = 1`
- `fail = 2`

已知风险仍然集中在：

- `VCTK masculine` 侧方向分数仍然偏低；
- `LibriTTS feminine` 至少有一条样本出现了 `rms_drift_gt_1p5db`。

## 当前状态

`v2` 已完成：

- 正式包导出
- 评审队列生成
- GUI 入口 smoke
- 电平复核

随后已完成正式听审，主观结果很明确：

- `8/8 reviewed`
- `effect_audible: yes=5, maybe=2, no=1`
- `direction_correct: maybe=5`
- `artifact_issue: yes=1, slight=5`

结合人工描述，当前可以把 `v2` 的主观失效模式写清楚：

- `female -> male`：更像“闷在小瓶子里说话”
- `male -> female`：更像“刻意增加高频”
- 两边都显得假，且没有真正碰到目标共鸣结构

因此 `LPC v2` 虽然已经跨过“可辨识”阈值，但当前更接近“可辨识的错误变化”，不应再视为健康主线。

## 下一步

1. 当前不再继续沿 `LPC pole edit` 直接加力。
2. 若仍保留 `LPC / LSF` 路线，应升级表示与参数化方式，而不是继续沿当前极点代理峰平移硬推。
3. 下一步更合理的是切到 `cepstral envelope` 对照线，或进入显式 `LSF` 参数化原型。
