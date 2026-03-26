# Stage0 Singing 听审结果与 Speech Pivot v1

## 本轮听审结论

当前已完成两轮 `singing` 试听：

- `tmp/stage0_rule_listening_pack/v1/`
- `tmp/stage0_rule_listening_pack/v2/`

人工听审结论一致：

- 全部样本均无可感知差异

这意味着：

- `v1` 静态 6 段 band-gain 太弱
- `v2` 即使把强度整体拉到约 `5x`，人耳仍然认为没有有效差异
- 当前这条 `singing -> 静态 band-gain -> 听审` 路线，至少在现有配置下不值得继续反复微调

## 对样本性别感知的补充解释

虽然试听包的源样本结构是：

- 一部分 `male -> feminine`
- 一部分 `female -> masculine`

但人工听感上，这些专业 singing 样本很多会表现为：

- 偏 female
- 或偏中性

这并不奇怪，原因更可能是：

- 专业演唱本身已经带来强烈的共鸣、发声位置和风格统一化
- style / technique 对听感性别的影响，可能强于当前规则试图推动的那一点静态 EQ

所以当前 `singing` 域并不适合作为“最先验证人耳可感知差异”的主战场。

## 为什么现在更适合转到 speech

相较于 `singing`，`speech` 更适合做下一轮主观验证，原因是：

1. 内容和发声方式更自然，专业技巧干扰更少
2. style 条件远弱于 `singing`
3. 人耳对 `speech` 的性别感知更直接
4. 一旦有差异，更容易判断是“音色方向变化”，而不是演唱风格变化

## 当前阶段性判断

当前可以先定一个阶段性结论：

- `singing` 路线暂不继续做静态 6 段 band-gain 的强度微调
- 下一步优先切到 `speech-first`

## 建议的下一步

1. 基于 `speech` 子集单独做一版试听包
2. 优先挑 `speech` 中更干净、时长稳定、性别感知清楚的样本
3. 在 `speech` 上重新验证：
   - 静态 band-gain 是否终于可感知
   - 如果仍然不可感知，再决定是否彻底放弃这条静态 EQ 路线
