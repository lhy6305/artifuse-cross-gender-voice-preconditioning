# 表示层路线：LSF 参数化原型 v6

## 背景

到 `v5` 为止，`LSF` 主线已经明确排除了两种不正确的 masculine 代理：

1. `brightness_down`
   - 有方向，但容易把 `female -> male` 做成发闷 / 瓶子音
2. `brightness_down + presence bypass`
   - 空气感回来一些，但方向性和 effect 也一起塌掉

因此 `v6` 的目标不再是继续调亮度，而是直接改 masculine 的目标定义。

## v6 的新假设

`v6` 把 `female -> male` 从：

- `brightness_down`

改成：

- `formant_lowering_preserve_air`

也就是说，这一轮不再试图让整体谱更暗，而是试图只改变：

1. 更低的下部 formant geometry
2. 更宽的低阶 `LSF` pair spacing
3. 同时尽量不动 `F3`

## 新实现

这轮新增了两部分底层能力：

1. `LSF` 成对编辑新增 `pair_width_ratios`
2. 自动量化新增 `formant_lowering_preserve_air` 评分分支

对应文件：

- `scripts/build_stage0_speech_lsf_listening_pack.py`
- `scripts/build_stage0_rule_review_queue.py`

## v6 machine-only sweep

本轮 machine-only 搜索位于：

- `scripts/run_lsf_machine_sweep.py --preset v6`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v6/lsf_machine_sweep_pack_summary.csv`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v6/LSF_MACHINE_SWEEP_V6.md`

最佳变体为：

- `lower_geom_v6b`

机器侧结果：

- `avg auto_quant_score = 81.13`
- `avg auto_direction_score = 70.97`
- `avg auto_effect_score = 87.46`
- `strong_pass = 5`
- `borderline = 3`
- `fail = 0`

这说明：

1. 新 family 没有被 machine gate 否掉
2. 它也没有回到 `v5` 那种“保空气感但方向没了”
3. 当前至少已经形成了重新进入人工的资格

## v6 的正式收敛

当前把 `lower_geom_v6b` 正式收敛为：

- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v6.json`

其中最关键的变化只在 masculine 侧：

- `action_family = formant_lowering_preserve_air`
- `center_shift_ratios = [0.97, 0.88, 1.00]` 或 `[0.96, 0.88, 1.00]`
- `pair_width_ratios = [1.08, 1.20, 1.00]` 或 `[1.06, 1.22, 1.00]`

也就是说：

- `F3` 基本保持中性
- 真正的动作集中在 `F2` 和 pair width

## 当前产物

- 正式配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v6.json`
- 正式听审包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v6/`
- 摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v6/listening_pack_summary.csv`
- 队列：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v6/listening_review_queue.csv`
- 量化摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v6/listening_review_quant_summary.md`

## 当前判断

`v6` 是到目前为止第一版满足下面三个条件的 masculine 路线：

1. 不继续把 male 近似成 broad dark tilt
2. 不再只靠 bypass 把高频硬混回
3. machine gate 仍然明确通过

因此当前最合理的下一步就是正式听审。

## 下一步

1. 用标准入口打开 `LSF v6` 正式听审：
   - `.\scripts\open_stage0_speech_lsf_review_gui.ps1 -PackVersion v6`
2. 若 `female -> male` 的“发闷 / 瓶子音”明显缓解，而 effect 仍可辨，则 `LSF` 主线继续保留。
3. 若主观仍然失败，再考虑把 `LSF` 家族从“中心位移”进一步升级到真正的带宽 / 几何建模。 
