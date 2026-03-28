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

## v6 正式听审结果

`LSF v6` 的正式听审已经完成，结果位于：

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v6/listening_review_queue.csv`

结果摘要：

1. `8/8 reviewed`
2. `effect_audible = yes 2 / maybe 6 / no 0`
3. `strength_fit = too_weak 8 / 8`
4. 本轮没有新增主导性伪影备注

因此 `v6` 的结论不是“路线错误”，而是：

- `formant_lowering_preserve_air` 这条新 masculine family 仍然成立
- 但它进入正式人审时的整包强度统一偏弱

## 当前判断

`v6` 已经完成了它的任务：

1. 证明了新的 masculine 目标函数可以维持方向
2. 证明了当前矛盾已经收缩到“强度不足”
3. 为下一拍给出了明确动作：先提强，再送下一轮人审

## 下一步

1. 不再重复送同强度的 `v6.x` 包做人审。
2. 先按 `too_weak` 主观结果把整包强度整体提高，再做下一版正式候选。
3. 下一版已切到 `LSF v7`，详见 `docs/63_representation_layer_lsf_probe_v7.md`。
