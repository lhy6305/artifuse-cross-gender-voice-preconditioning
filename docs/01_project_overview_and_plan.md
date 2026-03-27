# 项目总览与阶段计划

## 项目标识
- 当前仓库名：`artifuse-cross-gender-voice-preconditioning`
- 项目代号：`RGP-Pre`
- 仓库角色：`Artifuse` 系列中的一个研究子项目，聚焦 RVC 跨性别前置属性修正。

## 一句话目标
在尽量不破坏内容、节奏和主音高结构的前提下，对输入音频施加轻量、条件化、可解释的共鸣/谱包络修正，以改善 RVC 跨性别转换中的干瘪、薄和腔体感不匹配问题。

## 当前仓库现状
- 已有高层设计文档：`initial_design.md`
- 已有阶段 0/1 实验设计：`docs/10_stage0_stage1_experiment_design.md`
- 已有公开数据集候选清单：`docs/11_public_dataset_shortlist.md`
- 已有初版数据资产清单输出入口：`scripts/build_dataset_inventory.py`
- 已有初版 `utterance_manifest` 输出入口：`scripts/build_utterance_manifest.py`
- 已有首轮盘点结果：`docs/12_dataset_inventory_first_pass.md`
- 已有固定评测集 v1 规则文档：`docs/13_fixed_eval_sampling_v1.md`
- 已有结构化数据资产输出：`data/datasets/_meta/dataset_inventory.csv`、`data/datasets/_meta/utterance_manifest.csv`
- 已有固定评测集 v1 清单：`experiments/fixed_eval/v1/fixed_eval_manifest_v1.csv`
- 已有固定评测集 v1 增强清单与巡检表：`experiments/fixed_eval/v1/fixed_eval_manifest_v1_enriched.csv`、`experiments/fixed_eval/v1/fixed_eval_review_sheet_v1.csv`
- 已有固定评测集 v1 review pack 与 GUI 巡检入口：`experiments/fixed_eval/v1/review_pack/`、`scripts/open_fixed_eval_review_gui.ps1`
- 已基于首轮听审生成固定评测集 `v1_1`：`experiments/fixed_eval/v1_1/`
- 已有只审替换样本的 GUI 入口：`scripts/open_fixed_eval_v1_1_replacements_gui.ps1`
- 已基于最终 maybe 决议生成固定评测集 `v1_2`：`experiments/fixed_eval/v1_2/`
- 已有只审 `v1_2` 新替换样本的 GUI 入口：`scripts/open_fixed_eval_v1_2_replacements_gui.ps1`
- `v1_2` 新替换样本已补听通过，当前固定评测集终稿位于：`experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv`
- 已有 clean 主分析子集：`data/datasets/_meta/utterance_manifest_clean_speech_v1.csv`、`data/datasets/_meta/utterance_manifest_clean_singing_v1.csv`
- 已有 clean 子集说明：`docs/14_clean_analysis_subsets_v1.md`
- 已有阶段 0 运行环境基线说明：`docs/15_stage0_runtime_environment_v1.md`
- 已有阶段 0 基线分析说明与入口：`docs/16_stage0_baseline_analysis_v1.md`、`scripts/run_stage0_baseline_analysis.py`
- 已有阶段 0 full 手动入口：`scripts/run_stage0_baseline_full.ps1`
- 已有阶段 0 baseline pilot 输出：`experiments/stage0_baseline/v1_pilot/`
- 已有阶段 0 pilot 中文解释文档：`docs/17_stage0_pilot_interpretation_v1.md`
- 已有阶段 0 baseline full 输出：`experiments/stage0_baseline/v1_full/`
- 已有阶段 0 full 中文解释文档：`docs/18_stage0_full_interpretation_v1.md`
- 已有阶段 0 full 报告脚本与图表入口：`scripts/build_stage0_full_report.py`、`experiments/stage0_baseline/v1_full/stage0_full_report_v1.md`、`experiments/stage0_baseline/v1_full/plots/`
- 已有阶段 0 候选信号短名单：`docs/19_stage0_candidate_signal_shortlist_v1.md`
- 已有阶段 0 方向性规则草案：`docs/20_stage0_directional_rule_draft_v1.md`、`experiments/stage0_baseline/v1_full/directional_rule_draft_v1.csv`
- 已有阶段 0 候选规则配置：`docs/21_stage0_rule_candidate_config_v1.md`、`experiments/stage0_baseline/v1_full/rule_candidate_v1.csv`、`experiments/stage0_baseline/v1_full/rule_candidate_v1.json`
- 已有阶段 0 候选规则 selector 原型：`scripts/select_stage0_candidate_rules.py`、`experiments/stage0_baseline/v1_full/rule_selector_preview_summary_v1.md`
- 已有阶段 0 band-gain 原型：`docs/22_stage0_band_gain_profile_prototype_v1.md`、`scripts/build_stage0_band_gain_profiles.py`、`experiments/stage0_baseline/v1_full/rule_candidate_band_gain_profiles_v1.json`
- 已有阶段 0 最小规则前置器原型：`docs/23_stage0_rule_preconditioner_prototype_v1.md`、`scripts/apply_stage0_rule_preconditioner.py`、`scripts/build_stage0_rule_listening_pack.py`
- 已有阶段 0 规则试听量化与 GUI：`docs/24_stage0_rule_review_quant_gui_v1.md`、`scripts/build_stage0_rule_review_queue.py`、`scripts/stage0_rule_review_gui.py`、`scripts/open_stage0_rule_review_gui.ps1`
- 已有 `cmd` 兼容启动入口：`scripts/open_stage0_rule_review_gui.cmd`
- 已记录 singing 听审结果与 speech pivot：`docs/25_stage0_singing_listening_outcome_and_speech_pivot_v1.md`
- 已有 speech-first 试听包构建与 GUI 入口：`scripts/build_stage0_speech_listening_pack.py`、`scripts/open_stage0_speech_review_gui.ps1`、`scripts/open_stage0_speech_review_gui.cmd`
- 已有 speech-first 试听包说明：`docs/26_stage0_speech_listening_pack_v1.md`
- 已有 speech envelope warp 原型与 GUI 入口：`scripts/build_stage0_speech_envelope_listening_pack.py`、`scripts/open_stage0_speech_envelope_review_gui.ps1`、`scripts/open_stage0_speech_envelope_review_gui.cmd`
- 已有静态 EQ null result 与 envelope warp pivot 说明：`docs/27_stage0_static_eq_null_result_and_envelope_warp_pivot_v1.md`
- 已有 speech envelope warp `v2` 配置：`experiments/stage0_baseline/v1_full/speech_envelope_warp_candidate_v2.json`
- 已有 speech resonance tilt 原型与 GUI 入口：`scripts/build_stage0_speech_resonance_listening_pack.py`、`scripts/open_stage0_speech_resonance_review_gui.ps1`、`scripts/open_stage0_speech_resonance_review_gui.cmd`
- 已有 envelope warp 听审反馈与 resonance tilt pivot 说明：`docs/28_stage0_envelope_warp_feedback_and_resonance_tilt_pivot_v1.md`
- 已有 speech formant anchor 原型与 GUI 入口：`scripts/build_stage0_speech_formant_listening_pack.py`、`scripts/open_stage0_speech_formant_review_gui.ps1`、`scripts/open_stage0_speech_formant_review_gui.cmd`
- 已有 resonance tilt 听审反馈与 formant anchor pivot 说明：`docs/29_stage0_resonance_tilt_feedback_and_formant_anchor_pivot_v1.md`
- 已有 post-envelope/world 的新 formant-aware pivot 说明：`docs/35_stage0_post_envelope_world_formant_pivot_v1.md`
- 已有表示层转型说明：`docs/36_representation_layer_pivot_v1.md`
- 已有 LPC 编辑与重建原型说明：`docs/37_representation_layer_lpc_edit_probe_v1.md`
- 已有更强的 LPC v2 原型说明：`docs/38_representation_layer_lpc_edit_probe_v2.md`
- 已有 cepstral envelope 对照原型说明：`docs/39_representation_layer_cepstral_envelope_probe_v1.md`
- 已有表示层主线断点：`docs/40_representation_layer_lsf_then_vtl_checkpoint_v1.md`
- 已有 LSF 参数化原型说明：`docs/41_representation_layer_lsf_probe_v1.md`
- 已有 VTL warping 原型说明：`docs/42_representation_layer_vtl_warping_probe_v1.md`
- 已有 VTL warping v2 原型说明：`docs/43_representation_layer_vtl_warping_probe_v2.md`
- 已有阶段 0 轻量前置修正 phase gate 文档：`docs/30_stage0_lightweight_preconditioning_phase_gate_v1.md`
- 已有 speech source-filter / vocal-tract morph 原型与 GUI 入口：`scripts/build_stage0_speech_vocal_tract_listening_pack.py`、`scripts/open_stage0_speech_vocal_tract_review_gui.ps1`、`scripts/open_stage0_speech_vocal_tract_review_gui.cmd`
- 已有 source-filter / vocal-tract morph 说明：`docs/31_stage0_source_filter_vocal_tract_morph_v1.md`
- 已有 WORLD 重合成副作用结论与 STFT delta pivot 说明：`docs/32_stage0_world_resynthesis_artifact_and_stft_delta_pivot_v1.md`
- 已有 speech WORLD-guided STFT delta 原型与 GUI 入口：`scripts/build_stage0_speech_world_stft_delta_listening_pack.py`、`scripts/open_stage0_speech_world_stft_delta_review_gui.ps1`、`scripts/open_stage0_speech_world_stft_delta_review_gui.cmd`
- 已有阶段 1 RVC 串联评测 pivot 说明：`docs/33_stage1_rvc_cascade_eval_pivot_v1.md`
- 已有阶段 1 RVC 串联评测桥：`experiments/stage1_rvc_eval/v1/rvc_target_registry_v1.json`、`scripts/build_stage1_rvc_cascade_manifest.py`、`scripts/run_stage1_rvc_cascade_batch.py`、`scripts/run_stage1_rvc_cascade_batch.ps1`
- 已有阶段 1 RVC 串联听审清单与 GUI 入口：`scripts/build_stage1_rvc_cascade_review_queue.py`、`scripts/open_stage1_rvc_cascade_review_gui.ps1`、`scripts/open_stage1_rvc_cascade_review_gui.cmd`
- 已有听审稀疏标注汇总脚本：`scripts/build_listening_review_rollup.py`
- 已有表示层 probe 入口：`scripts/run_representation_layer_probe.py`、`scripts/run_representation_layer_probe.ps1`
- 已有 LPC 编辑听审包构建与 GUI 入口：`scripts/build_stage0_speech_lpc_listening_pack.py`、`scripts/open_stage0_speech_lpc_review_gui.ps1`、`scripts/open_stage0_speech_lpc_review_gui.cmd`
- 已有 cepstral envelope 听审包构建与 GUI 入口：`scripts/build_stage0_speech_cepstral_listening_pack.py`、`scripts/open_stage0_speech_cepstral_review_gui.ps1`、`scripts/open_stage0_speech_cepstral_review_gui.cmd`
- 已有 LSF 听审包构建与 GUI 入口：`scripts/build_stage0_speech_lsf_listening_pack.py`、`scripts/open_stage0_speech_lsf_review_gui.ps1`、`scripts/open_stage0_speech_lsf_review_gui.cmd`
- 已有 VTL 听审包构建与 GUI 入口：`scripts/build_stage0_speech_vtl_warping_listening_pack.py`、`scripts/open_stage0_speech_vtl_review_gui.ps1`、`scripts/open_stage0_speech_vtl_review_gui.cmd`
- 已有表示层 pilot 输出：
  - `experiments/representation_layer/v1_fixed_eval_pilot/`
  - `experiments/representation_layer/v1_clean_speech_probe/`
- 已有 LPC v1 听审包输出：
  - `artifacts/listening_review/stage0_speech_lpc_listening_pack/v1/`
- 已有 LPC v2 听审包输出：
  - `artifacts/listening_review/stage0_speech_lpc_listening_pack/v2/`
- 已有 cepstral v1 听审包输出：
  - `artifacts/listening_review/stage0_speech_cepstral_listening_pack/v1/`
- 已有 LSF v1 听审包输出：
  - `artifacts/listening_review/stage0_speech_lsf_listening_pack/v1/`
- 已有 VTL v1 听审包输出：
  - `artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/`
- 已有 VTL v2 听审包输出：
  - `artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v2/`
- 听审包与听审结果当前已迁到正式目录：`artifacts/listening_review/`；`tmp/` 不再作为长期保留位点
- 根目录已有可调用解释器：`python.exe`（当前可用）
- 已有本地预训练资产：`pretrained_rvc_firefly_fp32/`
- 已约定本地 RVC 工作目录：`Retrieval-based-Voice-Conversion-WebUI-7ef1986/`，允许为训练/测试修改代码，但不纳入当前 Git。
- 已建立实验记录与关键产物保留位点：`reports/daily/`、`experiments/`、`artifacts/checkpoints/keep/`
- 根目录 `tmp/` 作为统一临时产物落点，默认可随时清空
- 已建立日报模板：`reports/daily/0000_template.md`
- 当前已有首版依赖锁定说明：`requirements-stage0-analysis.txt`

## 当前阶段
阶段名：表示层建模 pivot（由前置模块研究升级）

当前目标：
1. 不再继续扩 `stage0` 轻量前置器同族变体，而是转向可解释表示层本身。
2. 比较 `WORLD envelope / LPC envelope / cepstral proxy` 哪种表示更稳定承载性别相关 tract / resonance 信息。
3. 先验证表示的分离度与时间连续性，再决定后续编辑与重建路线。
4. 将项目目标从“VC 前置模块”升级为“可解释的人声表示与操控”。

## 当前结论
- 本仓库适合采用“文档先行、脚本后补”的轻量起步方式。
- 当前仓库名定为 `artifuse-cross-gender-voice-preconditioning`。
- `RGP-Pre` 可以继续作为内部设计代号使用。
- 除 `artifacts/checkpoints/keep/` 中少量关键 checkpoint 外，本地权重与索引文件不应进入版本控制。
- 本地 RVC 工作目录应整体保持忽略状态，即使内部代码会被修改。
- 数据集下载包与解压 `raw/` 树只留本地，仓库内只保留脚本、来源说明和 `data/datasets/_meta/` 中的结构化清单。
- `reports/daily/`、`experiments/`、`artifacts/checkpoints/keep/` 是后续恢复进度的固定落位。
- 三套已解压数据都可以进入第一轮盘点，但 `VocalSet` 必须只选一套 canonical tree 计数。
- 第一轮主分析集可先定为 `VCTK + VocalSet`，`LibriTTS-R` 作为第二 `speech` 集做一致性检查。
- 第一版 `dataset_inventory.csv` 和 `utterance_manifest.csv` 已经生成，可直接作为后续脚本输入。
- 固定评测集 v1 先按 `96` 条结构化方案冻结，再在后续版本中补响度和 F0 等更细筛选条件。
- 固定评测集 v1 manifest 已经生成，可直接作为人工巡检和后续基准对比入口。
- 固定评测集 v1 的轻量声学特征与人工巡检工作表已生成，可以开始系统化清洗评测集。
- 固定评测集 v1 的 review pack 和 GUI 已就绪，可以从高优先级样本开始低成本听审。
- 已根据首轮听审移除 `11` 条不适合作为固定评测基准的样本，并自动补成 `v1_1`。
- 已对 `v1_1` 中的 6 条 `maybe` 做最终裁决：保留 2 条轻微瞬态干扰样本，移除 4 条技巧性 singing 样本，并自动补成 `v1_2`。
- `v1_2` 的 4 条新增替换样本已全部补听通过，当前固定评测集没有残留 `maybe`。
- `clean_speech_v1` 和 `clean_singing_v1` 已生成，可作为阶段 0/1 的保守分析入口。
- 阶段 0 baseline 已有首个可运行入口，当前 `pilot` 在 `256 speech + 256 singing` 规模上跑通，且特征提取成功率为 `100%`。
- 阶段 0 `full` 入口已补上并行、断点续跑、可见进度和 PowerShell 手动入口，可以拆成 `speech -> singing -> finalize` 三步执行。
- 阶段 0 `full` 已跑完，当前 `15100 speech + 2038 singing` 特征提取成功率为 `100%`。
- 阶段 0 `full` 已补第一版报告、图表和稳健分桶摘要，当前可直接进入候选信号筛选。
- 阶段 0 第一版候选信号已经收缩到 `spectral centroid` 与 `log_centroid_minus_log_f0` 主线，`rms / silence / voiced_ratio` 暂保留为分析监控指标。
- 阶段 0 第一版方向性规则草案已经形成，当前建议先只从 `singing` 域的稳定 style 和高区/低区条件开始保守启用。
- 阶段 0 第一版候选规则配置已导出为 CSV/JSON，当前可以直接对接最小规则前置器原型。
- 阶段 0 规则 selector 原型已跑通，当前 `clean_singing_v1` preview 覆盖率与 `median_split` 预期一致。
- 阶段 0 band-gain 原型已经形成，当前 `brightness_up / brightness_down` 已映射到 6 粗频带的保守 gain 模板。
- 阶段 0 最小规则前置器原型已跑通，当前已生成一版 `tmp/stage0_rule_listening_pack/v1/` 试听包。
- 阶段 0 试听环节已补量化评分与 GUI，当前可以把原音/处理音差异和人工听审写回同一张表。
- 规则试听 GUI 启动入口已改为默认复用已有队列表，避免每次打开前都被量化预处理阻塞。
- 已生成更激进的 `v2` band-gain profile 与试听包，当前可直接对比 `v1 / v2` 两轮听感。
- `singing v1 / v2` 两轮听审均无可感知差异，当前应优先转向 `speech-first`。
- `speech-first` 首轮量化已跑通，当前 `LibriTTS-R` 与 `VCTK` 的响应不一致，说明静态 EQ 在 speech 上开始有信息，但还不是稳定规则。
- `speech-first static EQ` 的 `8` 条人工听审也已完成，结果仍是 `8/8 no audible difference`，当前静态 6 段 EQ 可视为阶段性 `null result`。
- 下一步已切到 `speech voiced-envelope-warp` 原型，不再继续微调静态 6 段 EQ。
- `speech envelope warp v1` 已出现“部分样本可感知，但整体仍偏弱”的人工结果，说明这条路线比静态 EQ 更有前景。
- `speech envelope warp v2` 已生成，当前应优先对 `v2` 做下一轮听审，而不是再次改路线。
- `speech envelope warp v2` 听审后已确认：`female` 侧容易变成“窄带且不自然”，`male` 侧变化仍偏小，因此当前已转向 `speech broad-resonance tilt`。
- `speech broad-resonance tilt v1` 已生成，当前应优先验证它是否比 envelope warp 更自然、但仍可感知。
- `speech broad-resonance tilt v1` 人工听审已确认“自然但无感”，说明这条路线安全但仍然太弱。
- `speech formant anchor v1` 已生成，但机器侧先验比 resonance tilt 更弱，当前应把它当作新的探索分支，而不是已验证更优路线。
- `speech formant anchor v1` 的人工听审也已确认“无感但无伪影”，当前 `static EQ / envelope warp / resonance tilt / formant anchor` 这整个轻量频谱前置家族可视为阶段性 `null result`。
- 下一步不再建议继续堆同类轻量频谱变体，而应做阶段门选择：转更强的 source-filter / vocal-tract 路线，或收缩前置器职责为安全归一化。
- `speech source-filter / vocal-tract morph v1` 已跑通，当前 `8` 条样本的机器侧量化第一次明显进入高改变量区间，说明这条路线至少在作用层级上强于轻量频谱修正。
- 当前 `vocal-tract morph v1` 的主要风险集中在 `female -> masculine` 方向仍可能反向，因此下一步优先级已经收缩成“先听审，再决定这条路线是继续调参还是继续升级方法”。
- `speech source-filter / vocal-tract morph v1` 的人工听审已确认：主要听到的是底噪和瞬态脏声，人声目标方向基本没有起来，因此 `WORLD full resynthesis` 当前可视为实现层面的失败，而不是单纯参数没调好。
- 为避免把重合成噪声误当成“有效变化”，后续已改成 `WORLD analysis only + voiced STFT magnitude delta`，即保留原始相位和时域细节，只借 WORLD 提供谱包络差分。
- `speech WORLD-guided STFT delta v1` 已跑通，当前机器侧显示“保真明显更好，但方向性接近 0 且多为反向”，说明这版首先是去掉噪声成功了，但是否有听感价值仍需人工确认。
- `speech WORLD-guided STFT delta v1` 的人工听审也已确认：无可感知差异，但无失真/不自然；至此“前置器单独试听”已经不足以继续作为主 gate。
- 当前已恢复到设计稿中的正式主指标：看 `前置器 + RVC` 串联后是否整体改善，而不是要求前置器自己单独就有明显耳感。
- 阶段 1 的 RVC 串联评测桥已经跑通，当前本地 `fzjv2.pth` 可对固定样本做 `raw / preconditioned` 成对推理，并支持 manifest 断点续跑。
- 当前 `stage1_rvc_cascade_eval v1` 已完成 `16/16` 条推理，并已整理成 `8` 条 `raw->RVC vs preconditioned->RVC` 的成对听审队列，可直接进入人工比较。
- 但由于 `RVC` 目标说话人性别本身可能影响主观判断，当前人工口径已临时回切为“先只审模块本体修正前后”，不把 cascade 听感当作本轮第一判断依据。
- 共用听审 GUI 已同步切到该口径：默认按 `source vs preconditioned` 听，移除 `审核人`，改为左侧文件列表 + 可拖宽度 + 右侧滚动详情。
- 当前已回查各 `stage0` / `stage1` 听审队列，确认主观结果基本收敛：
  - `speech static EQ / resonance tilt / formant anchor / WORLD-guided STFT delta` 仍以“无可感知差异”为主；
  - `envelope warp v1` 是当前唯一进入“部分可感知”区间的方法，但结论仍偏弱，且 `keep` 只在少数 `masculine` 样本上给到 `maybe`；
  - `envelope warp v2` 虽比 `v1` 更可感知，但已开始稳定出现 `slight` 级不自然，尤其不适合作为当前保守主线；
- `vocal-tract morph v1` 虽然 `8/8` 可感知，但同时 `8/8` 明确为方向错误且有明显伪影，应继续排除；
- `stage1 cascade` 队列当前也已全部标成 `reviewed`，但字段填写明显不完整，暂不足以支持正式阶段结论。
- 当前已不再把这些空字段视为“漏填”；它们按用户口径属于稀疏标注的一部分，后续应通过汇总脚本解释，而不是回头机械补表。
- 当前已生成第一版听审汇总：`artifacts/listening_review_rollup/v1/`
- 按该汇总的当前判断：
  - `stage0_speech_listening_pack/v1`、`resonance v1`、`formant v1` 可冻结为 `null_result`
  - `stage0_speech_vocal_tract_listening_pack/v1` 可冻结为 `reject`
  - `stage0_speech_envelope_listening_pack/v1` 可保留为 `watch`
  - `stage0_speech_envelope_listening_pack/v2` 仅能保留为 `watch_with_risk`
  - `stage1_rvc_cascade_eval/v1` 当前只保留为 `watch` 级参考，不上升为正式主线结论
- 在修正 `stage0` GUI 播放口径并将听审包迁到 `artifacts/listening_review/` 后，已对受影响的 4 个分支完成复听：
  - `stage0_speech_listening_pack/v1`：仍为 `null_result`
  - `stage0_speech_resonance_listening_pack/v1`：仍为 `null_result`
  - `stage0_speech_formant_listening_pack/v1`：仍为 `null_result`
  - `stage0_speech_world_stft_delta_listening_pack/v1`：从 `null_result` 上调为 `watch`
- 当前 `WORLD-guided STFT delta v1` 的最新人工结果是：`8/8 reviewed`，其中 `audible_yes=2`、`audible_maybe=2`、`audible_no=4`，且已审样本里未出现显式伪影报告；但可辨识样本仍普遍被标为 `too_weak`，暂不足以单独升级为主线方法。
- 当前已正式设定并行比较清单：`docs/34_stage0_parallel_envelope_vs_world_comparison_v1.md`
- 当前并行比较的两条新候选已导出到正式听审目录：
  - `artifacts/listening_review/stage0_speech_envelope_listening_pack/v3/`
  - `artifacts/listening_review/stage0_speech_world_stft_delta_listening_pack/v2/`
- 在 `v3 / v2` 听审后，已确认两条线共同问题是“变化仍偏弱，只能 barely 分辨”；因此当前已切到 `audibility stress test`：
  - `artifacts/listening_review/stage0_speech_envelope_listening_pack/v4/`
  - `artifacts/listening_review/stage0_speech_world_stft_delta_listening_pack/v3/`
- 在 `v4 / v3` 听审后，已进一步确认：
  - `envelope warp v4` 虽然已稳定可辨，但主观方向整体反转；
  - `WORLD-guided STFT delta v3` 主观方向正确，但总体仍明显偏弱；
  - 因此当前已继续导出：
    - `artifacts/listening_review/stage0_speech_envelope_listening_pack/v5/`
    - `artifacts/listening_review/stage0_speech_world_stft_delta_listening_pack/v4/`
- 当前阶段自动量化里的 `direction` 指标只保留为弱参考；主观听审已优先于该指标，特别是在 `envelope / world_stft_delta` 两条线上。
- `stage0_speech_envelope_listening_pack/v5` 听审后已确认：
  - `5/8 audible_yes`
  - `0/8 audible_maybe`
  - `3/8 audible_no`
  - 主观方向已纠正回来，且整体几乎无明显伪影
  - 但听感更接近“直接拉伸音调/音色重心”，关键共鸣结构改变仍不够强
  - 因此这条线可保留为 `watch_with_risk`，但风险不再是伪影，而是“作用机理偏离目标”
- `stage0_speech_world_stft_delta_listening_pack/v4` 听审后已确认：
  - `4/8 audible_yes`
  - `4/8 audible_maybe`
  - `0/8 audible_no`
  - 但伪影统计已显著升高：`artifact_yes=4`、`artifact_slight=4`
  - 同时主观上性别改变程度仍不高
  - 因此这条线当前应从 `watch` 下调为 `reject`
- 到这一轮为止，主线判断已进一步收敛：
  - `envelope warp` 证明“可通过较强整体音色/音调感变化影响性别感知”，但未击中核心共鸣目标
  - `WORLD-guided STFT delta` 证明“继续加差分会先带来伪影，再带来有限收益”，不适合继续做主线
- 因此当前已启动新的 `formant-aware` pivot：
  - `artifacts/listening_review/stage0_speech_formant_listening_pack/v2/`
  - 目标是更明确地搬动局部共鸣结构，同时继续锁住相位与 `f0` 主体感
- `stage0_speech_formant_listening_pack/v2` 听审后已确认：
  - `8/8 audible_no`
  - 未出现值得记录的伪影问题
  - 说明即使升级到更强的三锚点 formant-aware 原型，当前实现仍未跨过可感知阈值
- 因此到目前为止，`stage0` 轻量前置器族的最终收口可以写成：
  - `static EQ / resonance tilt / formant anchor v1 / formant anchor v2`：`null_result`
  - `WORLD-guided STFT delta`：`reject`
  - `envelope warp`：`watch_with_risk`，但风险点是“更像整体音调/音色拉动，未击中核心共鸣目标”
- 因此当前已正式转向表示层研究，不再把“前置模块小修正”作为主问题。
- 表示层第一轮 probe 已在两组数据上跑通：
  - fixed-eval pilot：`experiments/representation_layer/v1_fixed_eval_pilot/`
  - clean-speech 子集：`experiments/representation_layer/v1_clean_speech_probe/`
- 当前 probe 的第一版比较结果：
  - `WORLD cheaptrick envelope`：分离度整体偏弱，不适合作为当前优先表示
  - `LPC envelope`：在 `LibriTTS-R` 上分离度最强，`separation_ratio ≈ 7.29`
  - `MFCC / cepstral proxy`：跨 `LibriTTS-R / VCTK` 的稳定性相对更均衡
- 因此下一步最值得继续的两条表示候选是：
  - `LPC / LSF` 路线
  - `cepstral envelope` 路线
- `LPC residual-preserving pole edit v1` 已完成第一版实现，并已导出正式听审包：
  - `stage0_speech_lpc_listening_pack/v1`
  - 当前机器侧先验显示 `feminine` 侧响应更强，但 `masculine` 侧方向不稳
  - 修复重建增益 bug 后，人工听审结果为：`maybe=4`、`no=4`、`too_weak=8`
  - 因此它当前是“已进入可听审状态但仍明显过弱的第一表示层编辑原型”，还不是已验证可行的方法
- `LPC residual-preserving pole edit v2` 已作为更强版本导出：
  - `stage0_speech_lpc_listening_pack/v2`
  - 当前机器侧先验明显强于 `v1`：`avg auto_quant_score ≈ 80.19`、`strong_pass=5`
  - 主观听审已确认：它虽然更可辨识，但更像“瓶中感 / 刻意加高频”的假变化，没有命中目标共鸣
  - 因此当前 `LPC pole edit` 也应视为阶段性 `reject`
- `cepstral envelope v1` 已作为 `LPC` 之后的第一条对照主线导出：
  - `stage0_speech_cepstral_listening_pack/v1`
  - 当前实现是基于 clean speech 参考集的低阶倒谱 centroid 差分
  - 机器侧先验当前优于 `LPC v2`：`avg auto_quant_score ≈ 85.23`、`strong_pass=6`、`fail=0`
  - 主观听审已确认：整体影响仍偏弱，且更像伪影/假高频，尤其 `male` 侧已有噪声感风险
  - 因此它当前最多只能保留为 `watch_with_risk`，不能升格为新的健康主线
- `LSF v1` 已按断点约束作为下一条主线原型落地：
  - `stage0_speech_lsf_listening_pack/v1`
  - 当前实现改为显式 `LSF` 成对位移与间距约束，不再直接做 `pole edit`
  - 已完成正式包导出、量化队列生成、GUI smoke 与主观听审
  - 当前机器侧先验：`avg auto_quant_score ≈ 73.54`、`avg auto_direction_score ≈ 60.31`、`strong_pass=2`、`fail=2`
  - 主观听审结果：`effect_audible yes=2, maybe=2, no=4`，`artifact_issue slight=3`
  - 当前人工结论是“整体仍偏弱，且部分样本开始出现伪影”，因此没有形成足够正证据继续留在主线
- `VTL v1` 已作为 `LSF` 失败后的第二顺位主线落地：
  - `stage0_speech_vtl_warping_listening_pack/v1`
  - 当前实现不是 `WORLD full resynthesis`，而是 `WORLD analysis only + original-phase STFT reconstruction`
  - 与旧 `world_stft_delta` 的差异是：只在 tract 主频段内生效，并在高频做渐隐，同时做带内能量回平
  - 已完成正式包导出、量化队列生成、GUI smoke 与正式听审
  - 当前机器侧先验非常弱：`avg auto_quant_score ≈ 36.92`、`avg auto_direction_score ≈ 3.73`、`fail=8`
  - 主观听审结果：`effect_audible yes=3, maybe=4, no=1`，但备注显示局部低 `f0` 才可辨、`F0` 对齐版本伪影重、部分样本出现双声叠加感
  - 因此它当前不能升格为健康主线，只能视为“可辨但问题复杂”的高风险候选
- `VTL v2` 已按上述失效模式做定向修正：
  - `stage0_speech_vtl_warping_listening_pack/v2`
  - 去掉了 `dry/wet` 叠加，优先压低双声感
  - 放宽并平滑 tract band 覆盖
  - 把带内能量回平从 `100%` 改成部分回平
  - 已完成正式包导出、量化队列生成与 GUI smoke
  - 当前机器侧先验依然偏负：`avg auto_quant_score ≈ 39.26`、`avg auto_direction_score ≈ 0.10`、`fail=8`
  - 因此当前默认下一轮正式听审对象已切到 `VTL v2`
- 当前表示层主线断点已明确固定：
  - 先试 `LSF`
  - 若 `LSF` 仍无正证据，再试 `VTL / tract-length warping`
  - 在这两步完成前，不再回到 `pole edit / cepstral delta` 上继续抠细节

## 近期任务
1. 以 `scripts/build_listening_review_rollup.py` 为标准汇总入口，后续不再要求把稀疏标注手工补成满表。
2. 基于 `artifacts/listening_review_rollup/v1/` 正式冻结以下结论：
   - `static EQ / resonance tilt / formant anchor` 归入 `null result`；
   - `vocal-tract morph v1` 归入“方向错误且伪影明显”的排除项；
   - `envelope warp v1` 与 `WORLD-guided STFT delta v1` 保留为待定分支，但都不应直接升格为主线；
   - `envelope warp v2` 不继续沿原方向硬推。
3. 在模块本体结论冻结前，暂停把 `stage1 cascade` 当成正式 gate；如需继续，只把它作为次级参考，不先驱动路线切换。
4. 若基于当前汇总仍无新增正证据，则短期不再新增同族前置原型，而是转向“安全归一化”收缩方案或等待新的方法级 pivot。
5. 当前先执行最后一轮受控并行比较，只保留两个新包：
   - `envelope warp v3`
   - `WORLD-guided STFT delta v2`
6. 若 `v3 / v2` 仍只停留在 barely 可辨，则继续推进到更强的 `audibility stress test`，并在听审时不把轻微整体音色偏移直接记作伪影。
7. 当前停止继续扩 `WORLD-guided STFT delta` 变体；后续若继续推进，只保留它作为被否定对照。
8. 当前不再把 `envelope warp` 视为最终候选，而把它视为“可辨识上限参考”；下一步应转向更显式的共鸣/formant 结构修改，同时尽量锁住 `f0` 和谐波感。
9. `stage0_speech_formant_listening_pack/v2` 已完成听审且归入 `null_result`，当前停止继续扩 `stage0` 轻量前置器。
10. `envelope v5` 当前只保留为“可辨识上限参考”，不再作为继续扩展的编辑对象。
11. 下一步已改为表示层路线：
   - 基于 `representation_layer` probe 结果，优先推进 `LPC / LSF` 与 `cepstral envelope`
   - `WORLD envelope` 只保留为对照，不再做优先主线
12. 当前 `LPC v1` 听审包已就绪：
   - 入口：`scripts/open_stage0_speech_lpc_review_gui.ps1 -PackVersion v1`
   - GUI 已新增“处理音(F0 对齐原音)”试听按钮，可在判断共鸣变化前先排除音调偏移
   - 当前人工听审已确认这版整体仍偏弱；若继续保留 `LPC` 路线，下一步应显式加大编辑强度
   - 若加强后仍不可感知，则下一步优先转向 `cepstral envelope` 对照原型
13. 当前默认下一轮听审对象已切到 `LPC v2`：
   - 入口：`scripts/open_stage0_speech_lpc_review_gui.ps1 -PackVersion v2`
   - 这轮已完成主观听审，并确认它不是单纯 `v1` 太保守，而是当前编辑方式本身在往错误听感上走
   - 因此下一步不应继续只靠当前 `pole edit` 加参数推进
14. 当前默认下一轮听审对象已切到 `cepstral v1`：
   - 入口：`scripts/open_stage0_speech_cepstral_review_gui.ps1 -PackVersion v1`
   - 这轮已完成听审，并确认它虽比 `LPC v2` 平滑，但仍没有摆脱“假高频 / 伪影感”
   - 因此下一步应继续升级表示层，而不是继续沿当前轻量参数化硬推
15. 当前接班断点已冻结为：
   - `LSF` 是第一顺位主线
   - `VTL / tract-length warping` 是第二顺位备选
   - 未完成这两步前，不再回头继续堆 `pole edit / cepstral delta`
16. `LSF v1` 已完成建包、量化、入口 smoke 和正式听审：
   - 入口：`scripts/open_stage0_speech_lsf_review_gui.ps1 -PackVersion v1`
   - 当前主观结论是“整体强度仍不足，且部分样本已有伪影”
   - 因此下一步主线已切到 `VTL / tract-length warping`
17. 共用听审 GUI 的播放口径已回退到更保守默认：
   - `peak_norm` 默认关闭
   - 默认舒适音量改为 `70%`
   - 勾选后只做“按最大峰值拉伸”的简单归一，不再默认做响度 boost / limiter
18. `VTL v1` 已完成建包、量化与入口 smoke：
   - 入口：`scripts/open_stage0_speech_vtl_review_gui.ps1 -PackVersion v1`
   - 当前机器侧先验是：`fail=8/8`
   - 主观听审虽确认部分样本可辨，但备注显示存在局部生效、对齐伪影和双声感
   - 因此下一步不应直接加强参数，而应先围绕这些具体失效模式做更窄的实现修正
19. 共用听审 GUI 已移除全部自定义键盘快捷键：
   - 不再支持播放、保存、标记和切换条目的热键
   - 后续默认只保留鼠标交互，避免误触
20. `VTL v2` 已完成建包、量化与入口 smoke：
   - 入口：`scripts/open_stage0_speech_vtl_review_gui.ps1 -PackVersion v2`
   - 当前自动量化显示：`effect` 比 `v1` 更强，但 `direction` 进一步恶化
   - 因此这轮听审的重点不是“有没有变化”，而是验证双声感和方向错误是否仍然成立

## 当前阶段验收标准
- 上下文恢复入口可直接使用。
- `docs/` 中存在最小接班文档骨架。
- `.gitignore` 与 `.gitattributes` 能正确覆盖当前已知重资产类型，同时为关键 checkpoint 保留可控白名单。
- 所有新增文本文件均遵守 UTF-8 无 BOM 约束。
