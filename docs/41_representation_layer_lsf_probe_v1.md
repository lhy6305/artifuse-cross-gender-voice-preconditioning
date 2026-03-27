# 表示层路线：LSF 参数化原型 v1

## 背景

在 `docs/40_representation_layer_lsf_then_vtl_checkpoint_v1.md` 把主线强约束固定为：

- 先试 `LSF`
- 若 `LSF` 仍无正证据，再试 `VTL / tract-length warping`

之后，当前第一步已经从断点进入可运行原型阶段。

这版 `v1` 的目标不是证明 `LSF` 已经可用，而是先回答一个更具体的问题：

**把编辑对象从直接 `LPC pole edit` 切到显式 `LSF` 成对位移后，是否能减少此前两类主观失败模式：**

- `female -> masculine` 的“小瓶子音 / 闷化”
- `male -> feminine` 的“刻意加高频 / 假亮感”

## v1 的实现口径

脚本：

- `scripts/build_stage0_speech_lsf_listening_pack.py`

配置：

- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v1.json`

入口：

- `scripts/open_stage0_speech_lsf_review_gui.ps1`
- `scripts/open_stage0_speech_lsf_review_gui.cmd`

当前做法：

1. 逐帧做稳定化 `LPC` 分析，并转换到 `LSF`
2. 只在 voiced 帧上操作
3. 在 `F1 / F2 / F3` 代理搜索带内，选最接近带中心的 `LSF` 成对边界
4. 按方向做成对中心位移，而不是直接搬单个极点
5. 每次位移后强制执行 `LSF` 间距与边界约束，再回转成 `LPC`
6. 继续保留 residual-preserving 重建与时域 overlap-add

因此 `v1` 的工程假设是：

- `LSF` 的排序和间距约束，应该比直接极点编辑更稳定
- 若主观仍然失败，失败模式也应更容易归因到表示本身，而不是局部极点代理搜索带失真

## 当前产物

- 听审包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v1/`
- 摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v1/listening_pack_summary.csv`
- 队列：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v1/listening_review_queue.csv`
- 量化摘要：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v1/listening_review_quant_summary.md`

## 当前机器侧先验

当前 `v1` 已完成正式包导出、量化队列生成和 GUI 入口 smoke。

量化摘要如下：

- `avg auto_quant_score ≈ 73.54`
- `avg auto_direction_score ≈ 60.31`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score ≈ 65.63`
- `strong_pass = 2`
- `borderline = 4`
- `fail = 2`

当前机器侧图景比 `cepstral v1` 更分化：

- `LibriTTS feminine` 侧响应最强，已有两条 `strong_pass`
- `LibriTTS masculine` 侧整体处于中间区
- `VCTK masculine` 侧仍然最弱，当前两条都落在 `fail`

因此这版还不能被解释成“比前两条线稳定更优”，但至少已经形成了清晰的主观听审对象。

## 当前状态

`LSF v1` 当前已完成：

- 脚本、配置与入口建好
- 正式听审包导出
- 量化队列与摘要生成
- `.\scripts\open_stage0_speech_lsf_review_gui.ps1 -PackVersion v1 -AutoCloseMs 1200` smoke
- 正式主观听审完成

此外，脚本侧已做过一轮最小实现校验：

- `stable_lpc -> lpc_to_lsf -> lsf_to_lpc` 往返在随机帧上可稳定闭环
- 当前未发现 `LSF <-> LPC` 转换本身的明显数值错误

## 主观听审结果

当前 `LSF v1` 已完成：

- `8/8 reviewed`
- `effect_audible: yes=2, maybe=2, no=4`
- `artifact_issue: slight=3`

结合本轮人工结论，当前可以把失败模式写清楚：

- 整体强度仍然不够，尚未跨过可用阈值
- 部分样本已出现伪影，但收益没有同步起来
- 因此它没有给出比 `LPC v2 / cepstral v1` 更明确的正证据

也就是说，`LSF v1` 当前更接近：

- 方向上仍未形成可靠主观正反馈
- 强度上仍偏弱
- 代价上开始出现新伪影

这不足以支持继续沿当前 `LSF v1` 参数小修小补。

## 下一步

1. 当前不再继续沿 `LSF v1` 的现有参数做强度微调。
2. 按 `docs/40_representation_layer_lsf_then_vtl_checkpoint_v1.md` 的顺序约束，下一步主线切到 `VTL / tract-length warping`。
3. 听审 GUI 的播放语义也已同步回退为更保守口径：
   - 默认 `peak_norm=off`
   - 默认舒适音量 `70%`
   - 勾选后只做“按最大峰值拉伸”的简单归一，不再做额外响度 boost / limiter 语义
