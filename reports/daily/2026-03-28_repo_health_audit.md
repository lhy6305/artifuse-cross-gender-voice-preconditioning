# 2026-03-28 仓库健康度与规范性自检

## 今日目标

- 完成一次全仓库健康度、规范性和实验风险自检。
- 覆盖目录结构、文件组织、Git 跟踪边界、代码质量与实验结论污染风险。
- 把可当天安全修复的问题直接修掉，并落盘一份可交接的评估文档。

## 扫描范围

- 入口文档：
  - `docs/00_context_bootstrap.md`
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `docs/05_task_branch_map.md`
  - `initial_design.md`
  - `docs/10_stage0_stage1_experiment_design.md`
- 仓库结构与 Git：
  - 全量 `git ls-files`
  - `git status --short --ignored`
  - 顶层目录递归计数
  - 已跟踪大文件与超长文本统计
- 关键脚本：
  - `scripts/run_stage0_baseline_analysis.py`
  - `scripts/run_representation_layer_probe.py`
  - `scripts/build_stage1_rvc_cascade_manifest.py`
  - `scripts/run_stage1_rvc_cascade_batch.py`
  - `scripts/build_utterance_manifest.py`
  - `scripts/build_clean_analysis_subsets.py`
  - `scripts/sample_fixed_eval_set.py`
  - `scripts/build_stage0_rule_review_queue.py`
  - `scripts/build_stage0_speech_listening_pack.py`
  - `scripts/fixed_eval_review_gui.py`
  - `scripts/stage0_rule_review_gui.py`
- 边缘与运维文件：
  - `tools/maintenance/sandbox_zero_byte_cleanup.py`
  - `artifacts/listening_review/README.md`
  - `data/datasets/singing/vocalset/record.json`

## 今日完成

- 确认顶层职责边界基本清楚：
  - `docs/` 承担设计与接班文档
  - `experiments/` 承担结构化实验输出
  - `artifacts/` 承担长期保留的听审与 checkpoint 辅助产物
  - `tmp/` 继续保持临时区
- 确认 Git 忽略边界总体有效：
  - 本地 RVC 工作目录、预训练资产、原始/派生音频和数据集 `raw/` 树大多处于忽略状态
  - 当前无未提交修改；忽略视野中主要是本地大资产与音频副本
- 完成长期维护文件体量扫描：
  - `data/datasets/_meta/utterance_manifest.csv` 约 `58k` 行 / `12.4 MB`
  - `docs/01_project_overview_and_plan.md` 约 `473` 行
  - `initial_design.md` 约 `891` 行
  - 多个核心 Python 脚本位于 `400~660` 行区间
- 完成 Python 语法自检：
  - `python -m compileall scripts tools/maintenance/sandbox_zero_byte_cleanup.py` 通过
- 完成最小烟测：
  - `scripts/run_representation_layer_probe.py --max-rows 2`
  - `scripts/run_stage0_baseline_analysis.py --pilot --max-rows 2`
  - `scripts/build_stage1_rvc_cascade_manifest.py --no-include-processed --data-root data/datasets --target-reference-sample-count 1`
  - 三条链路均成功产出最小结果

## 已修复

### 1. 补齐仓库级编辑器约束
- 新增 `.editorconfig`
- 当前固定：
  - 文本默认 `utf-8`
  - `ps1/cmd/bat` 使用 `crlf`
  - 其余主文本默认 `lf`
  - 自动保留末尾换行并清理尾随空白

### 2. 修复 `stage1` 脚本里无法关闭的布尔参数
- `scripts/build_stage1_rvc_cascade_manifest.py`
- `scripts/run_stage1_rvc_cascade_batch.py`
- 之前的 `store_true + default=True` 使参数实际不可关闭；现已改为 `BooleanOptionalAction`

### 3. 修复重建命令与路径漂移
- `scripts/build_stage1_rvc_cascade_manifest.py`
  - README 中原先把 `.ps1` 入口当成 Python 脚本调用，现已修正
- `scripts/build_stage0_speech_listening_pack.py`
- `artifacts/listening_review/stage0_speech_listening_pack/v1/README.md`
  - 重建命令已从旧 `tmp/` 路径切回当前正式 `artifacts/listening_review/` 路径

## 关键发现

### 中风险 1. 全量 manifest 的主键不够稳
- `scripts/build_utterance_manifest.py` 目前用 `path.stem` 直接生成 `utt_id`
- 实测 `data/datasets/_meta/utterance_manifest.csv` 中存在重复键：
  - `m9_caro_vibrato`
  - 分别来自 `VocalSet` 的 `male8` 与 `male9`
- 影响：
  - 凡是把 `utt_id` 当全局唯一键的缓存/断点续跑逻辑都有潜在错配风险
  - 当前 clean 子集和已落盘 enriched CSV 未命中该重复项，所以本轮主链实验暂未直接受污染
- 建议：
  - 后续若继续依赖全量 manifest，应把主键升级为 `dataset + speaker + stem` 的稳定 ID
 - 处理进展：
   - 当前已引入稳定 `record_id`
   - `stage0 baseline`、`representation probe`、固定评测集重建链路和 `stage1` 清单已切到 `record_id`

### 中风险 2. Git 跟踪边界仍有一处规则外样本
- `data/datasets/speech/libritts_r/doc.tar.gz` 原先被 Git 跟踪
- 它与“数据下载包默认不纳管”的仓库边界不完全一致
- 虽然体积仅约 `318 KB`，但边界不清比体积更值得警惕
- 处理进展：
  - 当前已执行 `git rm --cached`
  - 本地文件仍可保留，但默认不再进入版本控制

### 中风险 3. 根目录仍有环境耦合的一次性脚本
- 原脚本已迁到 `tools/maintenance/sandbox_zero_byte_cleanup.py`
- 环境耦合问题仍在，但根目录信噪比已经恢复
- 后续只需继续确保主流程不依赖这类本地运维工具

### 低风险 4. 长文档与长脚本开始逼近维护阈值
- `initial_design.md` 已接近 `900` 行
- `docs/01_project_overview_and_plan.md` 已接近 `500` 行
- 多个表示层相关脚本超过 `500` 行，且同族脚本之间有明显模板化重复
- 当前还未到必须立刻重构的程度，但已经进入“继续长就应拆”的区间

### 低风险 5. 历史文档仍残留早期 `tmp/` 路径
- 已修正会继续生成错误路径的源码与当前 README
- 但历史日报和专题文档中仍保留若干当时真实存在的 `tmp/` 路径引用
- 这类历史记录不建议大量回写，以免打乱时间线；后续应在新的总览/评估文档里明确“正式位点已迁到 `artifacts/listening_review/`”

## 总体评估

- 目录结构：`良好`
  - 主干职责清楚，临时区与正式区分界明确
  - 少数边缘文件仍需迁位
- 文件组织：`中上`
  - 命名大多直观
  - 但长文档、长脚本和生成型大 CSV 已开始堆高维护成本
- Git 跟踪规范：`中上`
  - 大部分重资产边界守住了
  - 仍存在一处已跟踪压缩包和一个环境耦合脚本
- 代码规范：`中上`
  - UTF-8 读写习惯整体良好
  - 当前缺点主要是脚本重复度高、少量参数设计失真、局部异常处理偏宽
- 实验结论污染风险：`可控但需继续收敛`
  - 当前未发现会直接推翻既有 clean 子集与已落盘结果的致命逻辑错误
  - 但全量 manifest 主键不稳，属于后续必须清掉的结构性风险

## 新发现的问题 / 风险

- `scripts/run_representation_layer_probe.py` 的抽样策略在 `samples-per-cell > 0` 时偏向按 `utt_id` 字典序取前几条，代表性不如按时长/F0/centroid 的中位邻近抽样稳健
- `scripts/build_clean_analysis_subsets.py` 在超额 cell 内更偏向先取较短样本，可能会对 clean 子集的时长分布带来温和偏置
- `fixed_eval` / `stage0` 两套 GUI 都会在“尚未真正完成审核”的情况下把默认值写回当前行；由于 `review_status` 仍保留 `pending`，当前不会直接污染正式结论，但可读性上会让“未审行”看起来像半填表

## 产出落点

- `.editorconfig`
- `docs/01_project_overview_and_plan.md`
- `docs/02_pitfalls_log.md`
- `reports/daily/2026-03-28_repo_health_audit.md`
- `scripts/build_stage1_rvc_cascade_manifest.py`
- `scripts/run_stage1_rvc_cascade_batch.py`
- `scripts/build_stage0_speech_listening_pack.py`
- `artifacts/listening_review/stage0_speech_listening_pack/v1/README.md`

## 下一步

- 把 `utterance_manifest` 主键升级为稳定命名空间 ID，并评估是否需要连带升级固定评测集与听审包摘要中的 `utt_id`
- 为表示层 listening pack 脚本抽公共模块，优先收敛重复的音频加载、WORLD/F0 分析、README 生成和 summary 写盘逻辑
- 若 `docs/01_project_overview_and_plan.md` 继续增长，开始建立 `docs/archive/`
