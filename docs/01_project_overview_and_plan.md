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
- 根目录已有可调用解释器：`python.exe`（当前可用）
- 已有本地预训练资产：`pretrained_rvc_firefly_fp32/`
- 已约定本地 RVC 工作目录：`Retrieval-based-Voice-Conversion-WebUI-7ef1986/`，允许为训练/测试修改代码，但不纳入当前 Git。
- 当前还没有正式脚本、依赖锁定说明和数据清单。

## 当前阶段
阶段名：开题与仓库整备

当前目标：
1. 固化仓库命名、边界和文档入口。
2. 明确哪些内容应该进入 Git，哪些内容只保留本地。
3. 为后续环境冻结、数据盘点和脚本落地预留清晰位置。

## 当前结论
- 本仓库适合采用“文档先行、脚本后补”的轻量起步方式。
- 当前仓库名定为 `artifuse-cross-gender-voice-preconditioning`。
- `RGP-Pre` 可以继续作为内部设计代号使用。
- 本地权重与索引文件不应进入版本控制。
- 本地 RVC 工作目录应整体保持忽略状态，即使内部代码会被修改。

## 近期任务
1. 固定 Python/Torch/音频处理依赖集合，并把解释器路径与版本写入文档。
2. 检查并补齐 `Retrieval-based-Voice-Conversion-WebUI-7ef1986/` 的实际工作副本内容，确认它与当前仓库的联调入口。
3. 建立最小目录规划，例如 `scripts/`、`third_party/`、`tmp/`。
4. 开始做数据资产总表和固定评测集方案。

## 当前阶段验收标准
- 上下文恢复入口可直接使用。
- `docs/` 中存在最小接班文档骨架。
- `.gitignore` 与 `.gitattributes` 能正确覆盖当前已知重资产类型。
- 所有新增文本文件均遵守 UTF-8 无 BOM 约束。
