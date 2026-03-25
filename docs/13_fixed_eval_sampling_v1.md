# 固定评测集 v1 抽样规则

## 目标

建立一份可复跑、可审阅、可直接纳入 Git 的固定评测集清单，用于后续跨阶段比较前置修正策略是否真的改善了跨性别转换输入条件。

## v1 设计定位

- 先把评测集边界固定下来，再逐步补更细的声学筛选字段。
- v1 只依赖当前已有的 `utterance_manifest.csv` 字段，不假设已经有响度、F0、SNR 或人工质检标签。
- v1 是“结构化第一版”，不是最终版；后续可在不推翻整体桶划分的前提下升级到 v2。

## 基础过滤条件

- `quality_flag == ok`
- `duration_sec` 在 `3.0` 到 `10.0` 秒之间
- 仅使用当前已固定的 canonical tree：
  - `VCTK Corpus 0.92`：`*_mic1.flac`
  - `LibriTTS-R`：本地已解压的 `dev-clean` 与 `test-clean`
  - `VocalSet 1.2`：`data_by_singer`

## 评测桶定义

固定四个主桶：

1. `speech_female`
2. `speech_male`
3. `singing_female`
4. `singing_male`

时长再细分为三个桶：

1. `3-5s`
2. `5-7s`
3. `7-10s`

## v1 配额

总规模固定为 `96` 条。

### speech

- 每个性别 `24` 条。
- 每个性别内部再拆成：
  - `VCTK Corpus 0.92`：`12` 条
  - `LibriTTS-R`：`12` 条
- 每个数据集内部按时长桶均分：
  - `3-5s`：`4`
  - `5-7s`：`4`
  - `7-10s`：`4`
- 同一数据集同一性别内，单个说话人最多入选 `1` 条。

### singing

- 每个性别 `24` 条，全部来自 `VocalSet 1.2`。
- 时长桶均分：
  - `3-5s`：`8`
  - `5-7s`：`8`
  - `7-10s`：`8`
- 同一性别内，单个歌手最多入选 `3` 条。

## 选择策略

- 先按桶过滤候选。
- 每个时长桶内部，优先挑选时长更接近该桶中心值的样本：
  - `3-5s` 中心为 `4.0`
  - `5-7s` 中心为 `6.0`
  - `7-10s` 中心为 `8.5`
- 在此基础上按说话人/歌手做 round-robin，保证不会被少数人占满。
- 相同优先级下按 `utt_id` 和 `path_raw` 稳定排序，确保脚本多次运行结果一致。

## v1 已知局限

- 还没有响度均衡约束。
- 还没有 F0 可提取性约束。
- 还没有人工听检标签。
- `VocalSet` 的内容仍以 vocalise / technique / excerpt 为主，不等同于流行歌曲整句主唱。

## 输出位置

- 规则文档：`docs/13_fixed_eval_sampling_v1.md`
- 抽样脚本：`scripts/sample_fixed_eval_set.py`
- 输出清单：`experiments/fixed_eval/v1/fixed_eval_manifest_v1.csv`
- 特征增强脚本：`scripts/enrich_manifest_features.py`
- 人工巡检表脚本：`scripts/build_review_sheet.py`
- review pack 构建脚本：`scripts/build_review_pack.py`
- GUI 巡检程序：`scripts/fixed_eval_review_gui.py`
- GUI 启动脚本：`scripts/open_fixed_eval_review_gui.ps1`
- 增强清单：`experiments/fixed_eval/v1/fixed_eval_manifest_v1_enriched.csv`
- 巡检工作表：`experiments/fixed_eval/v1/fixed_eval_review_sheet_v1.csv`
- review pack：`experiments/fixed_eval/v1/review_pack/`

## 升级到 v2 的优先方向

1. 给 `utterance_manifest.csv` 补充响度、F0 成功率、静音比例、粗略能量统计。
2. 在固定桶不变的前提下，把 v1 的候选再筛成更稳的 v2。
3. 为固定评测集补人工听检备注列和“禁用样本”机制。
