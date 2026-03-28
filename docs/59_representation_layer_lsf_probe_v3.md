# 表示层路线：LSF 参数化原型 v3

## v2 正式听审结论

`LSF v2` 已完成正式听审，当前结果与 `v1` 不同，不能再归为 `8/8 no audible`：

- `8/8 reviewed`
- `effect_audible: yes=4, maybe=4, no=0`
- `strength_fit: too_weak=5`
- `artifact_issue: yes=1`

当前最关键的备注只有一条：

- `LibriTTS masculine -> feminine` 的一条样本出现一次瞬时明显伪影，其余部分正常

因此这轮可以把结论写得更具体：

1. `LSF` 这条线已经第一次稳定跨过“全包不可辨”的门槛。
2. 当前主要矛盾已从“完全听不见”变成“整体偏弱”。
3. 伪影目前还不是系统性崩坏，更像单点风险，需要在增强强度时顺手盯住。

## 为什么继续推进到 v3

既然 `v2` 已经给出：

- 全包 `yes / maybe`
- 且机器侧与人工侧方向一致

那么这条线当前不该收口，而应顺着主观备注继续做一次更窄的强化：

- 只加一点有效强度
- 尽量不放大 `Libri feminine` 的瞬时伪影

## v3 的 machine-first 搜索

本轮基于 `v2` 再做了一次 machine-only 定向 sweep：

- 脚本：`scripts/run_lsf_machine_sweep.py --preset v3`
- 总表：`experiments/stage0_baseline/v1_full/lsf_machine_sweep_v3/lsf_machine_sweep_pack_summary.csv`
- 摘要：`experiments/stage0_baseline/v1_full/lsf_machine_sweep_v3/LSF_MACHINE_SWEEP_V3.md`

本轮最优变体是：

- `order20_rescue_v3e`

其机器侧结果：

- `avg auto_quant_score = 82.81`
- `avg auto_direction_score = 74.67`
- `avg auto_effect_score = 78.63`
- `strong_pass = 6`
- `borderline = 2`
- `fail = 0`

相对 `LSF v2`：

- `avg auto_quant_score` 从 `78.85` 提高到 `82.81`
- `avg auto_direction_score` 从 `68.09` 提高到 `74.67`
- `avg auto_effect_score` 从 `73.71` 提高到 `78.63`

更关键的是，这次不只是单一 cell 抬升，而是首次做到整包 `fail = 0`。

## v3 的正式收敛

当前把 `order20_rescue_v3e` 正式收敛为：

- 配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v3.json`

`v3` 的核心变化：

1. 全部规则从 `order-18` 升到 `order-20`
2. 两个 masculine cell 再加一档强度
3. `VCTK masculine` 继续使用更低的搜索带和更紧的间距约束
4. `Libri feminine` 只做中等幅度增强，避免直接放大 `v2` 备注里的瞬时伪影

因此 `v3` 不是盲目“再加大”，而是按 `v2` 的主观备注做受控强化。

## 当前产物

- 正式配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v3.json`
- 正式听审包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v3/`
- 摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v3/listening_pack_summary.csv`
- 队列：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v3/listening_review_queue.csv`
- 量化摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v3/listening_review_quant_summary.md`

## 当前判断

到这一步，`LSF` 主线的状态已经变成：

- `v1`: 可辨但偏弱且有伪影
- `v2`: 全包可辨，但整体仍偏弱
- `v3`: 机器侧继续显著增强，且当前是第一版整包 `fail=0`

所以当前最合理的下一步不是再扫一轮机器，而是立刻做 `v3` 的正式听审。

## 下一步

1. 用标准入口打开 `LSF v3` 正式听审：
   - `.\scripts\open_stage0_speech_lsf_review_gui.ps1 -PackVersion v3`
2. 若主观终于跨过“强度足够”的门槛，则 `LSF` 进入第一条真正可继续精修的主线。
3. 若主观仍然只给出“可辨但偏弱”，则后续只保留更窄的强度/伪影折中搜索，不再回到大范围家族切换。
