# 表示层主线断点：停止继续抠 Linear Low-Rank Envelope Subspace

## 断点目的

这份断点用于防止后续推进时，又重新回到：

- `low-rank envelope subspace v2 / v3`
- 继续拧 `latent_dims / latent_mix / variance_mix / blend / smooth`
- 在同一套**线性 low-rank latent affine** 语义里继续做小修小补

当前需要固定的是一个更高层判断：

**学习型低维表示这一步已经迈出去了，但当前 linear low-rank envelope latent 仍然没有给出足够正证据。**

## 当前阶段结论

截至当前断点：

- `conditional_envelope_transport v1`：`8/8 no audible`
- `conditional_envelope_transport v2`：`8/8 no audible`
- `low-rank envelope subspace v1`：虽然机器侧先验升到 `avg auto_quant_score ≈ 52.72`，但正式听审仍然 `8/8 no audible`

因此当前不能再把问题理解成：

- `latent_dims` 还没调准
- `latent_mix` 再大一点就会出来
- `variance_mix / blend / time_smooth_frames` 再拧一轮就能跨过阈值

## 强约束

从现在开始，默认不再继续以下动作：

1. 不继续出常规 `low-rank envelope subspace v2 / v3`
2. 不再沿当前 linear subspace + affine latent mapping 家族继续抠局部参数
3. 不再把“继续加大线性 latent 位移强度”当成当前主线

## 下一步原则

下一步应满足至少一条：

1. 从 linear low-rank latent 升级到**nonlinear / neural envelope latent**
2. 不再只做 `dataset x gender centroid/std` 级别的静态 affine 映射，而是引入更强的**conditioned latent predictor / decoder**
3. 若继续保留可解释性，也应换到“nonlinear latent / learned decoder / basis-plus-residual”层级，而不是继续停在线性子空间

## 接班口令

> 不要继续抠 linear low-rank envelope subspace。`2026-03-28` 这轮正式听审已经给出 `8/8 no audible`，下一步该换到更强的 nonlinear / neural envelope latent 了。
