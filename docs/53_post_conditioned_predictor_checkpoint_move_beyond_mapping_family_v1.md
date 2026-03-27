# 表示层主线断点：停止继续抠 Envelope Mapping Family

## 断点目的

这份断点用于防止后续推进时，又重新回到：

- `conditioned neural envelope v2 / v3`
- 继续拧 `translator_hidden_dims / train_epochs / latent_mix / smooth`
- 在同一套“先学表示，再做 target mapping”的 envelope mapping 家族里继续小修小补

当前需要固定的是一个更高层判断：

**到目前为止，reference transport、linear low-rank、static neural latent、conditioned latent predictor 都已经给出连续负证据。**

## 当前阶段结论

截至当前断点：

- `conditional_envelope_transport v1`：`8/8 no audible`
- `conditional_envelope_transport v2`：`8/8 no audible`
- `low-rank envelope subspace v1`：`8/8 no audible`
- `neural envelope latent v1`：`8/8 no audible`
- `conditioned neural envelope v1`：`8/8 no audible`

因此当前不能再把问题理解成：

- 只是表示层还不够 nonlinear
- 只是 predictor 还不够 conditioned
- 再换一个 mapping 头，应该就能跨过阈值

## 强约束

从现在开始，默认不再继续以下动作：

1. 不继续出常规 `conditioned neural v2 / v3`
2. 不再沿整个 envelope mapping 家族继续抠局部参数
3. 不再把“先学表示、再做目标映射”当成当前主线

## 下一步原则

下一步应满足至少一条：

1. 从 mapping family 升级到**probe-guided / objective-driven 直接编辑**
2. 不再只优化“像目标表示”，而是直接优化“朝目标方向移动”的判别目标
3. 若继续保留 envelope 编辑，也应换到“direct residual optimization / discriminative objective”层级

## 接班口令

> 不要继续抠 envelope mapping family。到 `2026-03-28` 为止，reference、low-rank、static neural、conditioned predictor 都是 `8/8 no audible`，下一步该换到 probe-guided direct residual 了。
