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
- 已有阶段 0 轻量前置修正 phase gate 文档：`docs/30_stage0_lightweight_preconditioning_phase_gate_v1.md`
- 已有 speech source-filter / vocal-tract morph 原型与 GUI 入口：`scripts/build_stage0_speech_vocal_tract_listening_pack.py`、`scripts/open_stage0_speech_vocal_tract_review_gui.ps1`、`scripts/open_stage0_speech_vocal_tract_review_gui.cmd`
- 已有 source-filter / vocal-tract morph 说明：`docs/31_stage0_source_filter_vocal_tract_morph_v1.md`
- 根目录已有可调用解释器：`python.exe`（当前可用）
- 已有本地预训练资产：`pretrained_rvc_firefly_fp32/`
- 已约定本地 RVC 工作目录：`Retrieval-based-Voice-Conversion-WebUI-7ef1986/`，允许为训练/测试修改代码，但不纳入当前 Git。
- 已建立实验记录与关键产物保留位点：`reports/daily/`、`experiments/`、`artifacts/checkpoints/keep/`
- 根目录 `tmp/` 作为统一临时产物落点，默认可随时清空
- 已建立日报模板：`reports/daily/0000_template.md`
- 当前已有首版依赖锁定说明：`requirements-stage0-analysis.txt`

## 当前阶段
阶段名：阶段 0 听审验证，第一个 source-filter 原型已跑通

当前目标：
1. 验证 `speech source-filter / vocal-tract morph v1` 是否首次产生稳定可感知差异。
2. 如果可感知，则把问题收缩到方向控制与副作用约束。
3. 如果仍不可感知，则重新评估“独立前置器听感收益”是否值得继续追。
4. 评估是否把前置器目标收缩为安全归一化并服务下游模型。

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

## 近期任务
1. 完成 `tmp/stage0_speech_vocal_tract_listening_pack/v1/` 的人工听审。
2. 根据听审结果决定 `vocal-tract morph` 是进入 `v2` 调参，还是继续升级到更强的 source-filter / formant-aware 路线。
3. 如果人工仍判无感，则重新评估“独立前置器听感收益”是否值得继续追，并考虑把前置器目标收缩为安全归一化。
4. 评估是否把特征增强脚本扩到 `utterance_manifest.csv` 的更大子集。

## 当前阶段验收标准
- 上下文恢复入口可直接使用。
- `docs/` 中存在最小接班文档骨架。
- `.gitignore` 与 `.gitattributes` 能正确覆盖当前已知重资产类型，同时为关键 checkpoint 保留可控白名单。
- 所有新增文本文件均遵守 UTF-8 无 BOM 约束。
