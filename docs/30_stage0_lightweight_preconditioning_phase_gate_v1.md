# Stage0 Lightweight Preconditioning Phase Gate v1

## 结论先行

截至当前，阶段 0 已经完成以下人工听审链路：

1. `singing static 6-band EQ v1`
2. `singing static 6-band EQ v2`
3. `speech static 6-band EQ v1`
4. `speech envelope warp v1`
5. `speech envelope warp v2`
6. `speech broad-resonance tilt v1`
7. `speech adaptive formant-anchor v1`

综合结论：

- `static EQ`：无可感知差异
- `envelope warp`：能制造差异，但容易在 `female -> masculine` 上出现窄带、不自然感
- `resonance tilt`：自然，但无可感知差异
- `formant anchor`：自然，但无可感知差异

所以当前可以正式做阶段门判断：

- `lightweight spectral preconditioning` 作为“人耳可感知的独立前置修正”路线，得到阶段性 `null result`

## 这不代表什么

这不代表：

- 项目整体失败
- 性别共鸣无法迁移
- 前置器永远没用

它只代表：

- 当前这类“轻量、可解释、频谱侧的小修正”，不足以在人耳上稳定建立独立可感知的效果

## 这代表什么

它代表当前最合理的工程判断是：

1. 不再继续堆更多同类小变体
2. 轻量前置器更适合作为：
   - 安全归一化
   - 副作用控制
   - 下游模型输入整理
3. 真正的性别共鸣迁移，可能需要：
   - 更强的 source-filter / vocal-tract 方法
   - 更强的 formant-aware 方法
   - 或直接由更强的下游转换模型承担

## 建议的下一阶段路线

### 路线 A：Source-Filter / Vocal-Tract Morph

目标：

- 直接操作声道包络或等效 vocal-tract 参数

特点：

- 理论上最接近“改共鸣壳体”
- 可能终于跨过可感知阈值
- 实现复杂度明显更高

### 路线 B：前置器只做安全归一化

目标：

- 不再追求“人耳单独听出来”
- 只做对下游模型有帮助的稳定化处理

特点：

- 更符合当前已验证事实
- 风险低
- 但项目目标会收缩

### 路线 C：把共鸣迁移责任交给下游模型

目标：

- 前置器只提供安全、稳定输入
- 性别感知主要依赖更强的转换模型

特点：

- 工程上更现实
- 但“可解释前置修正”这条研究主线会弱化

## 当前建议

如果继续深挖研究价值，我建议优先：

- 进入 `路线 A`

如果当前更在意工程落地速度，我建议优先：

- 进入 `路线 B + C`

## 当前不建议做的事

当前不建议：

- 再做第 5 种轻量频谱小变体
- 继续只在 gain / warp / tilt 的微调上消耗时间

因为已有结果已经足够说明：

- 这类方法的主要问题不是“参数还差一点”
- 而是“作用层级不够”
