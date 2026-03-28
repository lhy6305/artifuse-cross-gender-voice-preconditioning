# 表示层路线：LSF 参数化原型 v2

## 背景

`LSF v1` 的正式听审已经确认：

- 整体仍偏弱；
- 部分样本已有伪影；
- 但机器侧并不差，尤其 `LibriTTS feminine` 与 `LibriTTS masculine` 已经显著高于大量后续 `envelope-only` 家族。

因此在 `docs/57_machine_first_review_gate_v1.md` 固定的新流程下，`LSF` 不适合被直接判死，而更适合先做一次 machine-only 定向 sweep，再决定是否值得重新进入人工。

## 这轮 sweep 的目标

这次不再随机开新家族，而是只回答一个更窄的问题：

**能否在不回到 `WORLD / VTL` 的前提下，把 `LSF v1` 中最弱的 `VCTK masculine` 单元抬起来，同时不明显压坏其它三个 cell。**

为此本轮新增：

- sweep 脚本：`scripts/run_lsf_machine_sweep.py`
- sweep 总表：`experiments/stage0_baseline/v1_full/lsf_machine_sweep_v2/lsf_machine_sweep_pack_summary.csv`
- sweep 摘要：`experiments/stage0_baseline/v1_full/lsf_machine_sweep_v2/LSF_MACHINE_SWEEP_V2.md`

## Sweep 结果

本轮共跑了 `6` 个变体，全部都通过当前 machine gate。

其中最优变体是：

- `order18_vctk_rescue_v2e`

对应机器侧结果：

- `avg auto_quant_score = 78.85`
- `avg auto_direction_score = 68.09`
- `avg auto_effect_score = 73.71`
- `strong_pass = 4`
- `borderline = 2`
- `fail = 2`

相对 `LSF v1`：

- `avg auto_quant_score` 从 `73.54` 提高到 `78.85`
- `avg auto_direction_score` 从 `60.31` 提高到 `68.09`
- `avg auto_effect_score` 从 `65.63` 提高到 `73.71`

更关键的是，之前最弱的 `VCTK masculine` 单元得到实质抬升：

- `LSF v1`: `avg 47.31`
- `order18_vctk_rescue_v2e`: `avg 58.92`

虽然它还没有完全摆脱弱单元，但当前提升已经足够大，不再属于“机器侧没有任何新信息”的情况。

## v2 的正式收敛

基于本轮 sweep，当前把 `order18_vctk_rescue_v2e` 正式收敛为：

- 配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v2.json`

`v2` 的核心变化只有两类：

1. 全部规则统一切到 `lpc_order = 18`
2. 单独对 `VCTK masculine` 做更窄的 rescue：
   - 下调三段搜索带
   - 强化 `F1 / F2` 中频成对下移
   - 保持 `LSF` 间距与边界约束

因此 `v2` 不是方法换代，而是一次严格受控的 machine-guided promotion。

## 当前产物

- 正式配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v2.json`
- 正式听审包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/`
- 摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/listening_pack_summary.csv`
- 队列：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/listening_review_queue.csv`
- 量化摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/listening_review_quant_summary.md`

## 当前判断

到这一步，`LSF` 这条线的状态已经从：

- `v1` 虽可辨但偏弱且有伪影

更新为：

- `v2` 已在 machine-first 流程下明确过 gate
- 并且过线不是只靠 `LibriTTS feminine` 单边高分撑起来
- 因此当前这版值得重新进入正式人工听审

## 下一步

1. 用标准入口打开 `LSF v2` 正式听审：
   - `.\scripts\open_stage0_speech_lsf_review_gui.ps1 -PackVersion v2`
2. 若主观仍然不给正证据，再把 `LSF` 整条线彻底收口。
3. 若主观首次给出稳定正证据，再围绕 `VCTK masculine` 单元继续做更窄的 `v2.x` 修正，而不是重新回到大范围扫参。
