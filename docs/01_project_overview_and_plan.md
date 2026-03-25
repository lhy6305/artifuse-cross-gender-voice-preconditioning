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
- 根目录已有可调用解释器：`python.exe`（当前可用）
- 已有本地预训练资产：`pretrained_rvc_firefly_fp32/`
- 已约定本地 RVC 工作目录：`Retrieval-based-Voice-Conversion-WebUI-7ef1986/`，允许为训练/测试修改代码，但不纳入当前 Git。
- 已建立实验记录与关键产物保留位点：`reports/daily/`、`experiments/`、`artifacts/checkpoints/keep/`
- 已建立日报模板：`reports/daily/0000_template.md`
- 当前还没有依赖锁定说明。

## 当前阶段
阶段名：数据准备第三步，固定评测集 v1 人工巡检链路已具备，开始向更大范围的 manifest 特征增强过渡

当前目标：
1. 基于 review pack 与 GUI 开始人工抽查。
2. 把同类特征逐步扩展到更大的 manifest 范围。
3. 为阶段 0 的预处理与统计脚本准备稳定输入边界。
4. 固定环境依赖与运行入口。

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

## 近期任务
1. 通过 GUI 只补听 `v1_1` 中新增替换的 `11` 条样本。
2. 评估是否把特征增强脚本扩到 `utterance_manifest.csv` 的更大子集。
3. 固定 Python/Torch/音频处理依赖集合，并补环境说明。
4. 开始把人工巡检结论写入日报和实验记录，而不是只停留在对话里。

## 当前阶段验收标准
- 上下文恢复入口可直接使用。
- `docs/` 中存在最小接班文档骨架。
- `.gitignore` 与 `.gitattributes` 能正确覆盖当前已知重资产类型，同时为关键 checkpoint 保留可控白名单。
- 所有新增文本文件均遵守 UTF-8 无 BOM 约束。
