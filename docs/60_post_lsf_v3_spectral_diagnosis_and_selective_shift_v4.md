# LSF v3 后续诊断：频谱确认与 selective-shift v4

## 背景

`LSF v3` 的正式听审结束后，主观备注已经把问题点得很清楚：

- `female -> male` 前几条样本出现“沉闷 / 瓶子音”
- 同时出现可感知伪影
- 用户明确指出：`female` 和 `male` 都存在高频，不能把 `male` 简化成“刻意压高频”

这使得当前需要回答的核心问题，不再是“还能不能再加强”，而是：

**当前 `female -> male` 是否事实上被错误实现成了系统性中高频下压。**

## 频谱诊断是否可行

可行，而且当前已经证明是必要的。

本轮新增诊断脚本：

- `scripts/plot_lsf_review_diagnostics.py`

输出位点：

- `artifacts/diagnostics/lsf_review_v3/diagnostic_summary.csv`
- `artifacts/diagnostics/lsf_review_v3/DIAGNOSTIC_SUMMARY.md`
- `artifacts/diagnostics/lsf_review_v3/*.png`

每条样本都导出三类图：

1. 原音 / 处理音 long-term average spectrum
2. `processed - original` 差分频谱图
3. `0-1.5k / 1.5-3k / 3-8k` 三段能量占比变化

当前结论是：单看主观描述还不够，但把这三类图一起看，就能把“发闷 / 瓶子音”落成明确的频带失效模式。

## 频谱诊断结论

在 `LSF v3` 上，`female -> male` 四条样本的平均频带变化为：

- `0-1.5k`: `+0.07 dB`
- `1.5-3k`: `-4.11 dB`
- `3-8k`: `-1.40 dB`

这说明当前实现虽然不是字面意义上的“砍掉全部高频”，但在工程效果上，确实把 `male` 近似成了：

- 中频显著下压
- 高频也有一档下压

这正是“发闷 / 瓶子音”的典型风险图景。

因此当前可以明确写下：

1. 现有 `brightness_down` 代理过于粗糙。
2. `female -> male` 不能继续等价成“整体变暗”。
3. 下一步应改成“只改 tract 相关的选择性共鸣结构”，而不是继续默认牺牲空气感。

## 量化规则修正

为了避免 machine gate 再次偏爱“变暗但不自然”的候选，本轮已修改：

- `scripts/build_stage0_rule_review_queue.py`

新增规则：

- 对 `brightness_down` 样本，若 `1.5-3k` 下压过大，增加惩罚
- 对 `brightness_down` 样本，若 `3-8k` 下压过大，增加惩罚
- 自动备注新增：
  - `presence_drop_gt_2db`
  - `brilliance_drop_gt_0p75db`

这意味着后续 machine sweep 不再只看“是否整体更暗”，而会主动排斥“暗得发闷”的方案。

## selective-shift v4 machine-only sweep

基于上述诊断，本轮没有直接进入人工，而是新增：

- `scripts/run_lsf_machine_sweep.py --preset v4`

输出位点：

- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v4/lsf_machine_sweep_pack_summary.csv`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v4/LSF_MACHINE_SWEEP_V4.md`

`v4` 的核心约束是：

- `female -> male` 不再下拉 `F3`
- 只在 `F1 / F2` 做 selective shift
- 优先保住高频空气感

## v4 当前结论

在新的惩罚规则下，`v4` 最好的变体是：

- `mid_only_v4b`

整包机器侧为：

- `avg auto_quant_score = 78.49`
- `avg auto_direction_score = 71.29`
- `avg auto_effect_score = 76.28`

但这并不代表它已经解决问题。

对 `female -> male` 四条样本继续拆开看，`mid_only_v4b` 仍然存在：

- `1.5-3k` 平均 `-5.11 dB`
- `3-8k` 平均 `-0.96 dB`

也就是说：

- `F3` 保留后，高频塌陷确实减轻了；
- 但 presence 区仍然被压得太多；
- “瓶子音 / 发闷” 风险并没有真正解除。

因此当前不应把 `v4` 直接晋级到正式人工听审。

## 当前断点

到这一步，`LSF` 主线已经从“听不见”升级到“能听见，但 masculine 代理方式错了”。

当前最合理的下一步不是继续盲扫强度，而是：

1. 放弃把 `female -> male` 近似成整体 `brightness_down`
2. 把 masculine 编辑改成更窄的 `presence-preserving tract shift`
3. 下一轮 machine-only 搜索应优先约束：
   - `3-8k` 基本不下压
   - `1.5-3k` 不再出现系统性 `-3~-6 dB` 级下降

换句话说，当前 `LSF` 不是收口，而是进入了新的实现问题：

**不是“强度不够”，而是 `male` 方向的目标函数定义错了。**
