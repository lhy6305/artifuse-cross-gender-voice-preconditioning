# 项目上下文恢复入口

## 当前仓库标识
- 当前仓库名：`artifuse-cross-gender-voice-preconditioning`
- 内部代号：`RGP-Pre`
- 当前定位：围绕 RVC 跨性别前置属性修正的研究设计、实验规划、文档沉淀与后续脚本实现子仓库。

## 当前仓库边界
- 应纳管内容：设计文档、实验计划、脚本、轻量配置、结构化摘要、日报、实验记录、少量关键 checkpoint。
- 默认不纳管内容：原始或派生音频、大型下载包、绝大多数模型权重和索引、私钥、一次性推送脚本、本地依赖副本。
- 当前已知本地资产：
  - `pretrained_rvc_firefly_fp32/`：本地预训练 RVC 资产，默认只留本地。
  - `Retrieval-based-Voice-Conversion-WebUI-7ef1986/`：本地可改 RVC 工作目录，用于训练/测试联调，但整个目录默认不纳入当前仓库 Git 追踪。
- 当前约定保留位点：
  - `data/datasets/_meta/`：结构化数据清单与样本级 manifest。
  - `reports/daily/`：日报、阶段小结、临时结论沉淀。
  - `experiments/`：实验配置、抽样规则、结果摘要、对比记录。
  - `artifacts/checkpoints/keep/`：少量关键 checkpoint 或索引，仅保留可用于恢复进度的里程碑版本。

## 读取顺序
每次开始新一轮工作，或历史上下文丢失时，按以下顺序恢复：

1. 本文档 `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `docs/05_task_branch_map.md`
5. `initial_design.md`
6. `docs/10_stage0_stage1_experiment_design.md`

如果上述文件不足以恢复上下文，再补做以下检查：

1. 查看仓库根目录当前文件结构。
2. 查看 `git status --short --ignored`，确认哪些是正式内容、哪些是本地资产。
3. 只在确有必要时再读取更细的实验输出或新建专题文档。

## 强制规范

### 1. 编码与文本读写
- 全部文本文件统一使用 UTF-8 无 BOM。
- 在 PowerShell 中读写文本时，必须显式指定 UTF-8。
- 推荐先执行：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding
```

- 读取文本优先使用 `Get-Content -Encoding utf8`。
- 写回文本优先使用 `Set-Content -Encoding utf8` 或明确支持 UTF-8 的编辑器。

### 2. Python 与运行环境
- 当前仓库根目录已有 `python.exe`，可作为默认解释器入口。
- 仅有解释器还不够；任何需要 Python、Torch、音频特征提取的任务，在正式开跑前仍要记录关键依赖版本和启动方式。
- 如果后续引入 `.venv/`、额外依赖锁文件或不同运行模式，必须在 `docs/01_project_overview_and_plan.md` 中同步登记。

### 3. Git 跟踪边界
- `.gitignore` 的目标不是“尽量多忽略”，而是明确区分：
  - 可恢复、可审阅、适合协作的轻量资产；
  - 重资产、敏感资产、本地依赖和一次性产物。
- 任何时候都不能把以下内容误纳管：
  - 私钥和认证材料；
  - 原始/派生音频；
  - 模型权重、索引、大型中间缓存；
  - 本地训练/测试用的 RVC 工作目录。
- 数据集的下载包与解压 `raw/` 树默认只留本地，仓库中只保留脚本、来源说明和结构化摘要。
- 关键 checkpoint 可以纳管，但必须放到 `artifacts/checkpoints/keep/`，且数量保持克制。
- 每次修改 `.gitignore` 后，至少核对一次 `git status --short --ignored`。

### 4. 文档维护纪律
- 项目推进不能只留在对话中，关键判断必须落盘。
- 至少持续维护以下文档：
  - 项目总览与阶段计划：`docs/01_project_overview_and_plan.md`
  - 踩坑与边界记录：`docs/02_pitfalls_log.md`
  - 任务/分支映射：`docs/05_task_branch_map.md`
- 当前仓库尚未建立归档区；只有在活跃文档明显变长后，才新增 `docs/archive/`。

### 5. 目录结构纪律
- 根目录只保留高信号入口材料，不长期堆放一次性实验文件。
- 后续新增内容时优先使用明确目录，例如：
  - `docs/`
  - `scripts/`
  - `reports/daily/`
  - `experiments/`
  - `artifacts/checkpoints/keep/`
  - `tools/`
  - `data/datasets/_meta/`
  - `third_party/` 放已说明用途的第三方参考代码
- 临时文件统一放入仓库根目录 `tmp/`。
- `tmp/` 视为可随时人工清空的临时区，不承载正式产物。

### 6. 决策与实验推进
- 当前阶段以“开题和仓库整备”为主，不直接假设模型训练或大规模实验已经开跑。
- 进入脚本实现前，先确认三件事：
  - 数据资产边界清楚；
  - 运行环境固定；
  - 评测与日志落盘方案明确。

### 7. 网络与外部依赖
- 如需下载依赖、拉取上游代码、安装新包或获取模型，先在文档中注明原因和版本来源，再由用户决定是否执行。
- 不把“可联网获取”当作默认前提写死到流程里。

## 文档状态维护规则
- 每完成一个子任务，至少更新一次 `docs/01_project_overview_and_plan.md`。
- 新发现的环境问题、编码问题或 Git 边界问题，及时补到 `docs/02_pitfalls_log.md`。
- 若后续形成真实分支策略或任务并行关系，再更新 `docs/05_task_branch_map.md`，不要提前写空泛流程图。
