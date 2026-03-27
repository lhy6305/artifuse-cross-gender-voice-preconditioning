# 表示层路线：VTL Warping 原型 v1

## 背景

在 `docs/41_representation_layer_lsf_probe_v1.md` 里，`LSF v1` 已经被主观确认成：

- 整体仍偏弱
- 部分样本开始出现伪影
- 没有形成比 `LPC v2 / cepstral v1` 更明确的正证据

因此按 `docs/40_representation_layer_lsf_then_vtl_checkpoint_v1.md` 的顺序约束，当前主线正式切到：

- `VTL / tract-length warping`

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_vtl_warping_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_vtl_warping_candidate_v1.json`

入口：

- `scripts/open_stage0_speech_vtl_review_gui.ps1`
- `scripts/open_stage0_speech_vtl_review_gui.cmd`

这版不是回到早期的 `WORLD full resynthesis`，而是保留较安全的外壳：

1. `WORLD analysis only`
2. 从 `cheaptrick envelope` 提取 tract-length warp 带来的平滑包络位移
3. 只把该位移施加到原始 `STFT magnitude`
4. 保留原始相位与原始细节
5. 只在 voiced 段启用

同时，这版比旧 `world_guided_stft_delta` 多加了三层约束：

- 只在 tract 主频段内生效
- 高频通过过渡带渐隐到 `0`
- 对活动频段做带内能量回平，避免整体亮暗倾斜被误当成 tract 变化

因此当前工程问题变成：

**如果把 warp 收紧成更像“声道长度变化”的频段受限包络位移，它是否会比旧 `world_stft_delta` 更像真正的 tract 变化，而不是泛化亮暗变化。**

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/`
- 摘要：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/listening_pack_summary.csv`
- 队列：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/listening_review_queue.csv`
- 量化摘要：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/listening_review_quant_summary.md`

## 当前机器侧先验

`VTL v1` 已完成：

- 正式包导出
- 量化队列生成
- `.\scripts\open_stage0_speech_vtl_review_gui.ps1 -PackVersion v1 -AutoCloseMs 1200` smoke

当前量化摘要非常保守，且结果偏负：

- `avg auto_quant_score ≈ 36.92`
- `avg auto_direction_score ≈ 3.73`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 20.96`
- `strong_pass = 0`
- `pass = 0`
- `borderline = 0`
- `fail = 8`

自动量化当前把它判成：

- 整体改变量偏弱
- 多数样本方向不足
- `LibriTTS` 两个 `feminine` 样本甚至触发了 `wrong_direction`

这说明当前 `VTL v1` 至少在机器侧还没有站住。

## 当前状态

`VTL v1` 当前已完成：

- 正式包导出
- 量化队列生成
- GUI smoke
- 正式主观听审完成

## 主观听审结果

当前 `VTL v1` 已完成：

- `8/8 reviewed`
- `effect_audible: yes=3, maybe=4, no=1`
- `artifact_issue: slight=3, no=2`
- `strength_fit: too_weak=1, ok=2`

但这轮的关键不在于“能不能听见”，而在于听见的到底是什么。

结合备注，当前失效模式已经比较清楚：

- 一部分样本只有在局部低 `f0` 段才可辨，说明效果不稳定，不能视为整段成立
- 多条样本的 `F0` 对齐试听版本出现了明显伪影，说明当前处理结果仍然夹带较强的音高相关副作用
- 至少两条样本的处理音出现了“像两个高低声部叠加”的轻微双声感

因此当前可以把这版结论写成：

- 虽然可辨识度比机器侧预期高
- 但变化并不稳定，且伴随新的伪影类型
- 现阶段还不能把它视为健康主线结果

## 下一步

1. 当前不应直接把 `VTL v1` 升格为可用方案。
2. 需要先基于本轮备注重新判断问题到底来自：
   - `VTL` 本身的方向设置
   - voiced mask / 频段约束不稳
   - 还是当前 `F0` 相关残留导致的双声感与对齐伪影
3. GUI 侧已同步移除全部自定义键盘快捷键，避免后续听审时误触。
