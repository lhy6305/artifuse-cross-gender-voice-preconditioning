# 表示层路线：LSF 参数化原型 v7

## 背景

`LSF v6` 的正式听审已经完成，结论不是方向错，也不是伪影主导失败，而是：

1. `8/8 reviewed`
2. `effect_audible = yes 2 / maybe 6 / no 0`
3. `strength_fit = too_weak 8 / 8`

也就是说，`v6` 已经维持住了可辨方向，但整包仍然统一偏弱。

## 新的流程约束

基于这次听审，当前不再接受“机器侧过 gate 但人审整包统一 too_weak”的候选直接原样送下一轮人工。

这轮已把新的流程信号写回：

- `scripts/build_listening_machine_gate_report.py`

新增字段：

- `reviewed_too_weak_rows`
- `strength_escalation_recommendation`
- `strength_escalation_reason`

当已听审包出现“绝大多数样本 `too_weak` 且伪影不主导失败”时，下一步默认动作改为：

- `escalate_strength_before_next_human`

## v7 的核心假设

`v7` 不再继续换 family，而是直接沿用 `v6` 已经相对正确的几何代理：

- `female -> male` 继续使用 `formant_lowering_preserve_air`
- `male -> female` 继续使用 `brightness_up`

但把正式人审前的目标改成：

1. 整包强度先整体上提一档
2. 不只补 masculine，feminine 也同步增强
3. 仍然避免回到 `brightness_down` 或 broad dark tilt

## v7 machine-only sweep

这轮搜索位于：

- `scripts/run_lsf_machine_sweep.py --preset v7`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v7/lsf_machine_sweep_pack_summary.csv`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v7/LSF_MACHINE_SWEEP_V7.md`

本轮共跑 `5` 个更强的 `v7` 变体，全部通过主 machine gate。

最佳变体为：

- `balanced_strong_v7d`

机器侧结果：

- `avg auto_quant_score = 86.47`
- `avg auto_direction_score = 81.05`
- `avg auto_effect_score = 97.17`
- `strong_pass = 5`
- `pass = 2`
- `borderline = 1`
- `fail = 0`

这说明：

1. `v7` 成功响应了 `v6` 的“整包过弱”反馈
2. 提强后没有把 pack 平均质量拉回 gate 以下
3. 当前值得重新进入正式人工听审

## v7 的正式收敛

当前把 `balanced_strong_v7d` 正式收敛为：

- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v7.json`

关键变化：

1. `feminine` 两组规则同步提强
   - `LibriTTS-R`: `center_shift_ratios = [1.15, 1.11, 1.07]`, `blend = 0.82`
   - `VCTK`: `center_shift_ratios = [1.16, 1.12, 1.08]`, `blend = 0.84`
2. `masculine` 仍保留 `formant_lowering_preserve_air`
   - `LibriTTS-R`: `center_shift_ratios = [0.97, 0.85, 1.00]`, `pair_width_ratios = [1.10, 1.24, 1.00]`, `blend = 0.92`
   - `VCTK`: `center_shift_ratios = [0.96, 0.85, 1.00]`, `pair_width_ratios = [1.08, 1.26, 1.00]`, `blend = 0.92`

## 当前产物

- 正式配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v7.json`
- 正式听审包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v7/`
- 摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v7/listening_pack_summary.csv`
- 队列：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v7/listening_review_queue.csv`
- 量化摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v7/listening_review_quant_summary.md`

## 当前判断

`v7` 是当前最符合新流程约束的正式候选：

1. 它直接回应了 `v6` 的主观失败模式
2. 它没有重新回到错误的 broad dark tilt 路径
3. 机器侧强度、方向和可感知性都比 `v6` 更高

## 下一步

1. 用标准入口打开 `LSF v7` 正式听审：
   - `.\scripts\open_stage0_speech_lsf_review_gui.ps1 -PackVersion v7`
2. 如果主观从“8/8 too_weak”提升到更合格的强度区间，继续在 `v7.x` 附近微调。
3. 如果提强后开始转成伪影主导失败，再把下一拍切到更细的带宽 / 几何约束，而不是继续线性加大 `blend`。
