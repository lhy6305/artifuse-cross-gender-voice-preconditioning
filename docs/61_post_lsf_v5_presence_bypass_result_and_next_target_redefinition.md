# LSF v5 结果：Presence Bypass 不足以修复 male 方向

## 背景

在 `docs/60_post_lsf_v3_spectral_diagnosis_and_selective_shift_v4.md` 里，`LSF v3` 的主观失败模式已经被收敛为：

- `female -> male` 不是单纯偏弱；
- 而是容易出现“发闷 / 瓶子音”；
- 频谱诊断也确认了当前 `male` 方向存在系统性的 `presence / brilliance` 下压。

因此本轮进一步追问的是：

**如果不再继续压中高频，而是把原始 presence / air 逐步旁路混回，`female -> male` 能不能既保空气感，又保住方向性。**

## 本轮新增

实现侧新增：

- `scripts/build_stage0_speech_lsf_listening_pack.py`

新增能力：

- `preserve_original_from_hz`
- `preserve_original_full_hz`
- `preserve_original_mix`

含义是：从某个频点开始，逐步把原始频谱混回处理结果，用于避免 `female -> male` 继续把高频空气感一起压塌。

Machine-only sweep 新增：

- `scripts/run_lsf_machine_sweep.py --preset v5`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v5/lsf_machine_sweep_pack_summary.csv`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v5/LSF_MACHINE_SWEEP_V5.md`

同时，自动量化也已同步加入新的惩罚：

- `presence_drop_gt_2db`
- `brilliance_drop_gt_0p75db`

对应文件：

- `scripts/build_stage0_rule_review_queue.py`

## v5 machine-only 结果

本轮最优变体是：

- `presence_bypass_plus_v5b`

但它的结论并不够好：

- `avg auto_quant_score = 63.41`
- `avg auto_direction_score = 49.52`
- `avg auto_effect_score = 52.06`
- `decision = borderline_review_optional`

也就是说，它没有通过当前主 gate。

## 关键发现

对 `female -> male` 四条样本拆开看，`v5` 的问题非常明确：

1. `3-8k` 下压已经显著减轻
2. 但 `1.5-3k` 仍普遍为明显负值
3. 更关键的是，方向性和可感知强度也一起掉下来了

例如 `presence_bypass_v5a`：

- `female -> male` 平均 `3-8k = -0.27 dB`
- 相比 `v3` 的 `-1.40 dB` 已明显改善

但与此同时：

- `female -> male` 平均 `auto_direction_score = 10.50`
- `female -> male` 平均 `auto_effect_score = 12.06`
- 四条 masculine 样本全都掉到 `fail`

因此当前结论很明确：

**单靠把 upper band 混回原音，虽然能减少“发闷”，但会把这条线的主要方向性一起冲掉。**

## 当前判断

到这一步，`LSF` 主线已经排除了两种不正确的 masculine 代理方式：

1. `v3` 路线：整体向下拉，方向有了，但容易发闷 / 瓶子音
2. `v5` 路线：高频旁路保真，空气感回来了，但方向性明显塌掉

这说明：

- 问题不再是“再找更好的 blend”
- 也不再是“再保一点高频”
- 而是当前 `male` 方向的目标函数本身定义得不对

换句话说，`male` 不能继续被近似成：

- `brightness_down`
- 或 `brightness_down + high-band bypass`

## 下一步

下一步应切到新的 machine-only 实现假设：

1. 不再把 `female -> male` 视为“整体变暗”
2. 不再只靠 `LSF` 中心位移解决 male 方向
3. 下一轮应改成更明确的：
   - `tract-shape / lower-formant geometry`
   - `pair-spacing / bandwidth`
   - 或其它不会自动牺牲 presence 的目标定义

当前结论是：

**`presence-preserving bypass` 只能证明“压高频不是正确答案”，但它还不是新的正确答案。**
