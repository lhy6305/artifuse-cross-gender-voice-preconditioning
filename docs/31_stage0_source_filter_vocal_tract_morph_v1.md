# Stage0 Source-Filter / Vocal-Tract Morph v1

## 目标

基于 `docs/30_stage0_lightweight_preconditioning_phase_gate_v1.md` 的阶段门判断，当前不再继续尝试轻量频谱小修正，而是直接进入更强的：

- `WORLD source-filter / vocal-tract morph`

核心原则：

1. 保留原始 `f0`
2. 用 `WORLD` 分解出 `source / filter`
3. 只对 `spectral envelope` 的频率轴做条件化 warp
4. 再由 `WORLD` 重合成

## 为什么这条路线和前面不同

前面的 `EQ / envelope warp / resonance tilt / formant anchor` 都还属于：

- 频谱侧轻量修补

这条路线则是：

- 显式进入 `source-filter` 层级

它更接近：

- 改 vocal tract 长度
- 改共鸣壳体

而不是：

- 在原谱上加一点 gain / tilt

## 当前原型

已经新增：

- `experiments/stage0_baseline/v1_full/speech_vocal_tract_morph_candidate_v1.json`
- `scripts/build_stage0_speech_vocal_tract_listening_pack.py`
- `scripts/open_stage0_speech_vocal_tract_review_gui.ps1`
- `scripts/open_stage0_speech_vocal_tract_review_gui.cmd`

临时目录：

- `tmp/stage0_speech_vocal_tract_listening_pack/v1/`

当前已实际生成：

- `tmp/stage0_speech_vocal_tract_listening_pack/v1/listening_pack_summary.csv`
- `tmp/stage0_speech_vocal_tract_listening_pack/v1/listening_review_queue.csv`
- `tmp/stage0_speech_vocal_tract_listening_pack/v1/listening_review_quant_summary.md`

## 当前参数

当前 `v1` 的核心参数是：

- `male -> feminine`：`warp_ratio > 1`
- `female -> masculine`：`warp_ratio < 1`
- `blend = 0.92 ~ 0.95`
- `frame_period_ms = 5.0`

直觉上：

- 女性向相当于更短 vocal tract
- 男性向相当于更长 vocal tract

## 当前机器侧结果

当前 `v1` 已在 `8` 条 `speech` 样本上跑完量化：

- `avg auto_quant_score = 70.44`
- `avg auto_direction_score = 56.07`
- `avg auto_preservation_score = 74.81`
- `avg auto_effect_score = 91.07`

分级结果：

- `strong_pass = 1`
- `pass = 3`
- `fail = 4`

当前边界很清楚：

- `male -> feminine` 两组样本是主要希望
- `female -> masculine` 两组样本仍有 `wrong_direction` 风险

所以这版的目标不是“已经可用”，而是验证：

- 更强的 source-filter / vocal-tract 操作，是否终于能在人工听审里稳定跨过可感知阈值
- 如果能听见，问题更可能收缩到“方向控制”和“副作用约束”

## 人工听审结果

人工听审已经完成，结论是否定的：

- 全部样本都出现明显底噪
- 可听到类似接线接触不良的瞬态干扰
- 人声本身没有形成有价值的目标方向变化

所以这版当前不再继续调 `warp_ratio / blend`，而是直接判定：

- `WORLD full resynthesis` 不适合作为阶段 0 的直接试听实现

后续已转向：

- `WORLD-guided voiced STFT delta`

对应说明见：

- `docs/32_stage0_world_resynthesis_artifact_and_stft_delta_pivot_v1.md`

## 启动命令

PowerShell:

```powershell
.\scripts\open_stage0_speech_vocal_tract_review_gui.ps1
```

`cmd.exe`:

```cmd
.\scripts\open_stage0_speech_vocal_tract_review_gui.cmd
```
