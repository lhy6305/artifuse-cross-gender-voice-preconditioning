# 表示层主线断点：停止继续抠 Reference Envelope Transport

## 断点目的

这份断点用于防止后续推进时，又重新回到：

- `conditional_envelope_transport v3 / v4`
- 继续拧 `nearest_k / transport_ratio / blend / smooth`
- 在同一套 reference retrieval / anchor transport 语义里继续做小修小补

当前需要固定的是一个更高层判断：

**reference-based conditional envelope transport 到当前为止，已经给出了足够负证据。**

## 当前阶段结论

截至当前断点：

- `conditional_envelope_transport v1`：`8/8` 不可辨识
- `conditional_envelope_transport v2`：改成更强的 `source-anchor -> target-anchor` 局部对比 delta 后，仍然 `8/8` 不可辨识

因此当前不能再把问题理解成：

- `nearest_k` 还没调准
- `transport_ratio` 再大一点就会出来
- `time_smooth_frames` 再收一档就能跨过阈值

## 强约束

从现在开始，默认不再继续以下动作：

1. 不继续出 `conditional_envelope_transport v3 / v4`
2. 不再沿 `reference retrieval / anchor transport` 家族继续抠局部参数
3. 不再把“继续加大倒谱包络搬运强度”当成当前主线

## 下一步原则

下一步应满足至少一条：

1. 从 reference-based 编辑升级到**学习型低维表示**
2. 编辑对象不再是“逐帧参考包络向量”，而是更稳定的**低秩子空间 / latent envelope**
3. 若继续保留可解释性，也应换到“learned subspace / basis / latent”层级，而不是继续做 reference pull / transport

## 接班口令

> 不要继续抠 reference envelope transport。两轮主观 `8/8 no audible` 已经足够，下一步该换到学习型低维包络表示了。
