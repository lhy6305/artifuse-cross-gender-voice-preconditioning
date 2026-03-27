# 表示层主线断点：停止继续抠 Static Neural Envelope Latent Mapping

## 断点目的

这份断点用于防止后续推进时，又重新回到：

- `neural envelope latent v2 / v3`
- 继续拧 `hidden_dims / latent_dims / latent_mix / variance_mix / blend / smooth`
- 在同一套**小型自编码器 + 静态 latent centroid/std 映射** 语义里继续做小修小补

当前需要固定的是一个更高层判断：

**表示层已经从 linear low-rank 升级到 nonlinear latent，但当前 static latent mapping 仍然没有给出足够正证据。**

## 当前阶段结论

截至当前断点：

- `conditional_envelope_transport v1`：`8/8 no audible`
- `conditional_envelope_transport v2`：`8/8 no audible`
- `low-rank envelope subspace v1`：`8/8 no audible`
- `neural envelope latent v1`：虽然已经换成 nonlinear autoencoder latent，但正式听审仍然 `8/8 no audible`

因此当前不能再把问题理解成：

- `hidden_dims` 还没调准
- `latent_dims` 再大一点就会出来
- `latent_mix / variance_mix / blend / smooth` 再拧一轮就能跨过阈值

## 强约束

从现在开始，默认不再继续以下动作：

1. 不继续出常规 `neural envelope latent v2 / v3`
2. 不再沿当前 static latent centroid/std mapping 家族继续抠局部参数
3. 不再把“继续加大 static latent 位移强度”当成当前主线

## 下一步原则

下一步应满足至少一条：

1. 从 static latent mapping 升级到**conditioned latent predictor**
2. 不再只做 `dataset x gender centroid/std` 级别的全局映射，而是引入更强的**content-aware latent translator**
3. 若继续保留 learned decoder，也应换到“predictor + decoder”或“basis-plus-residual”的条件化结构，而不是继续停在静态映射

## 接班口令

> 不要继续抠 static neural envelope latent mapping。`2026-03-28` 这轮正式听审已经给出 `8/8 no audible`，下一步该换到 conditioned latent predictor / learned decoder 了。
