# 跨性别共鸣属性预变换前置系统（RGP-Pre，V1.0）

## 当前角色

本文件现在只保留：

- 高层目标与边界摘要
- 当前应优先阅读的设计入口
- 完整历史设计稿的稳定引用

完整长稿已冻结到：

- `docs/reference/initial_design_full_v1.md`

这样做的原因很直接：

- 原始设计稿已经超过 `1100` 行
- 同时承担了“入口说明 / 完整设计 / 前期准备附录”三种职责
- 继续把它当作活文档维护，阅读和更新成本都过高

## 一句话目标

在尽量不破坏内容、节奏和主音高结构的前提下，对输入音频施加轻量、条件化、可解释的共鸣 / 谱包络修正，以改善 RVC 跨性别转换中的干瘪、薄和腔体感不匹配问题。

## 仍然有效的核心约束

- 这不是完整 VC 系统，而是 `RVC` 之前的前置修正模块。
- 不把任务简化成单一“男女均值差分向量”。
- 不让前置模块承担大幅 `pitch conversion` 主职责。
- 优先使用条件化、平滑、可控的包络 / 共鸣修改。
- 最终正式评价口径保持不变：
  - `前置模块 + RVC 串联后的整体改善`
  - 不是 `前置模块单独试听是否明显`

## 当前设计状态

- 这份 `V1.0` 设计稿仍有历史价值，但不再适合作为唯一活跃入口。
- 当前真正执行中的路线、结论和待办，已经转移到更细粒度的运行文档。
- 因此本文件保留为“设计总纲摘要”，不再继续累加实验流水账。

## 阅读顺序

如果你要恢复当前仓库状态，优先读：

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `docs/10_stage0_stage1_experiment_design.md`

如果你要看完整历史设计稿，再读：

- `docs/reference/initial_design_full_v1.md`

## 文档分工

- `initial_design.md`
  - 高层设计摘要
  - 只保留长期稳定、不会频繁变动的系统级口径
- `docs/reference/initial_design_full_v1.md`
  - 冻结保存的完整 `V1.0` 长稿
  - 供回溯原始设计推导时查阅
- `docs/01_project_overview_and_plan.md`
  - 当前仓库现状
  - 当前阶段结论
  - 近期任务与验收口径
- `docs/10_stage0_stage1_experiment_design.md`
  - 可执行实验设计细则
  - 字段、流程、输出、统计任务定义
- `docs/02_pitfalls_log.md`
  - 环境边界
  - Git 跟踪边界
  - 编码、资产、运维层踩坑

## 当前建议

- 不要再把新的实验过程直接追加进本文件。
- 若出现新的系统级设计变更，优先：
  - 更新 `docs/01_project_overview_and_plan.md` 的当前结论
  - 更新对应阶段设计文档
  - 只有在真正改变系统总纲时，才回写本文件

## 完整历史设计稿

- [完整设计稿：docs/reference/initial_design_full_v1.md](/F:/proj_dev/tmp/workdir4-2/docs/reference/initial_design_full_v1.md)
