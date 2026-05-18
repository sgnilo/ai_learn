---
layout: default
title: "Transformer 与 Attention"
---

# Transformer 与 Attention

## 学习状态

学习中。

## 当前理解

Transformer 是现代 LLM 的核心结构，Attention 让模型能够在上下文中建立 token 之间的关联。

它接在 embedding 后面：

```text
文本
-> tokenizer
-> token ids
-> embedding lookup
-> [batch_size, seq_len, hidden_size]
-> Transformer blocks
-> logits
-> 预测下一个 token
```

Transformer block 的核心任务是：

```text
让每个 token 的向量，吸收上下文里其他 token 的信息
```

现代 decoder-only LLM 通常由很多层 Transformer block 堆叠而成。每层大致保持输入输出形状一致：

```text
[batch_size, seq_len, hidden_size]
-> Transformer block
-> [batch_size, seq_len, hidden_size]
```

多层堆叠后，每个 token 的 hidden state 会从“初始 embedding 表示”逐步变成“结合上下文后的动态表示”。

## 核心概念

- Self-Attention
- Q / K / V
- Multi-Head Attention
- Positional Encoding / Position Embedding
- Feed Forward Network
- Residual Connection
- LayerNorm

## Transformer block 的主流程

一个简化的 Transformer block 可以理解为：

```text
输入 hidden states
-> Self-Attention
-> 残差连接
-> LayerNorm / RMSNorm
-> Feed Forward Network
-> 残差连接
-> LayerNorm / RMSNorm
-> 输出 hidden states
```

直觉上：

```text
Attention：横向看上下文，token 与 token 交互
FFN / MLP：纵向加工特征，增强每个 token 自己的表达能力
Residual：保留原始信息，并叠加新信息
Norm：稳定数值尺度，让深层训练更稳定
```

注意：真实模型可能采用 pre-norm 结构，也就是先 norm 再进入 attention / FFN：

```text
x = x + Attention(Norm(x))
x = x + FFN(Norm(x))
```

但从第一轮理解看，可以先抓住这个主干：

```text
Attention 和 FFN 是主要计算层
Residual 和 Norm 是稳定深层网络训练与信息传递的结构
```

## Attention 在做什么？

Self-attention 会为每个 token 计算它应该关注上下文里哪些 token。

如果一段序列有 `seq_len = 5`，attention 会得到类似：

```text
[5, 5]
```

的关注关系矩阵。可以类比成一张“每个 token 看每个 token 多少”的表：

```text
attention_scores[i][j]
= 第 i 个 token 应该关注第 j 个 token 多少
```

它不是简单乘法表，而是由 Query 和 Key 的相似度计算得到，再经过 mask、softmax 等步骤变成权重。

每个 token 最后会根据这些权重，从所有 token 的 Value 里加权汇总信息，得到融合上下文的新表示。

## Self-Attention 与跨上下文学习

Self-attention 只在当前输入上下文内部建立 token 间动态关系。

一次训练样本里：

```text
context A
-> embedding
-> Transformer blocks
-> self-attention 让当前 context 内 token 互相取信息
-> hidden states
-> logits
-> loss
-> 反向传播
-> 更新参数
```

这次更新会影响：

```text
出现过的 token 对应的 embedding 行
Wq / Wk / Wv
FFN 参数
输出层参数
其他全局参数
```

另一轮训练样本 `context B` 如果也包含相同 token，那么它也会通过当前上下文里的 attention 产生新的 hidden state，并继续影响 loss 和参数更新。

因此：

```text
同一个 token 在不同上下文中反复出现
-> 这些上下文共同塑造该 token 的 embedding 行和相关 Transformer 参数
-> 模型参数沉淀出这个 token 在不同语境中的统计规律
```

但要注意：

```text
token 不是直接连接不同上下文
共享参数才是连接不同上下文经验的载体
```

例如：

```text
river bank
bank account
```

这两个上下文不会在 attention 里互相看到。但它们会共同影响 `bank` 的 embedding 行和相关 Transformer 参数。最终模型可能学到 `bank` 有多义性，并在推理时根据当前上下文选择更合理的语义方向。

所以可以这样区分：

```text
self-attention：当前上下文内的信息融合
训练参数更新：跨样本、跨上下文规律的长期沉淀
hidden state：当前上下文里的临时动态结果
model parameters：跨上下文积累下来的长期能力
```

## Q / K / V 直觉

每个 token 的输入向量会通过可训练矩阵投影成三种向量：

```text
Q = Query
K = Key
V = Value
```

可以类比成检索：

```text
Query：我现在想找什么信息
Key：每个 token 提供的可匹配标签
Value：如果匹配上了，真正拿走的信息
```

计算过程：

```text
Q = X @ Wq
K = X @ Wk
V = X @ Wv
```

核心公式：

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

拆开看：

```text
QK^T：计算 token 之间的相关性分数
/ sqrt(d_k)：缩放，避免数值太大
softmax：把分数变成权重
乘 V：根据权重汇总信息
```

## Causal Mask

Decoder-only LLM 训练和生成时通常只能看过去，不能看未来。

```text
第 1 个 token 只能看第 1 个
第 2 个 token 只能看第 1~2 个
第 3 个 token 只能看第 1~3 个
```

这叫 causal mask。它保证模型做的是：

```text
基于已有上下文预测下一个 token
```

而不是偷看未来答案。

## Multi-Head Attention

Multi-head attention 让模型并行用多组 Q/K/V 从不同子空间看上下文。

如果：

```text
hidden_size = 4096
num_heads = 32
```

常见情况下：

```text
head_dim = 4096 / 32 = 128
```

每个 head 在自己的 `head_dim` 子空间里做 attention，最后把多个 head 的结果拼回 `hidden_size`。

直觉上：

```text
multi-head = 多个不同视角的 attention 并行工作
```

不同 head 可能偏向关注不同关系，例如局部短语、指代、语法、长距离依赖等。但真实 head 的含义不一定能被人类清晰命名。

## FFN / MLP

FFN 主要对每个 token 自己的表示做非线性加工。

常见形状：

```text
hidden_size -> intermediate_size -> hidden_size
```

例如：

```text
4096 -> 14336 -> 4096
```

Attention 负责 token 之间交换信息；FFN 负责在每个 token 内部把特征表达加工得更丰富。

## 输出到哪里？

很多层 Transformer block 后，输出形状仍然是：

```text
[batch_size, seq_len, hidden_size]
```

然后接 LM head：

```text
[batch_size, seq_len, hidden_size]
-> [batch_size, seq_len, vocab_size]
```

生成时通常看最后一个位置：

```text
logits[:, -1, :]
```

也就是基于当前上下文预测下一个 token 的概率分布。

## 待学习问题

- Q、K、V 分别代表什么？
- Attention 为什么能找到上下文里的相关信息？
- Multi-head attention 为什么有用？
- Transformer block 的完整计算流程是什么？
- causal mask 为什么是 decoder-only LLM 的核心约束？
- Residual 和 Norm 分别解决什么训练稳定性问题？
- FFN 为什么通常是参数量大户？

## 实践记录

### 2026-05-18：Transformer 总览

本轮完成的理解：

- Embedding 后的张量进入 Transformer，形状是 `[batch_size, seq_len, hidden_size]`。
- LLM 由很多层 Transformer block 堆叠，每层通常保持输入输出 shape 一致。
- Attention 横向计算 token 之间的关注关系，并汇总上下文信息。
- Self-attention 只连接当前上下文；不同上下文之间的规律通过共享参数更新沉淀下来。
- FFN / MLP 纵向加工每个 token 自身的特征表达。
- Residual 和 Norm 负责稳定信息传递和数值分布。
- 多层传递后，每个 token 的 hidden state 会逐步变成上下文相关表示。

练习代码段：

```text
x: [batch_size, seq_len, hidden_size]

x = x + Attention(Norm(x))
x = x + FFN(Norm(x))

output: [batch_size, seq_len, hidden_size]
```

## 关键代码

```text
Q = X @ Wq
K = X @ Wk
V = X @ Wv

Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

## 踩坑

- 不要以为 Transformer block 会改变主张量 shape；通常每层输入输出都是 `[batch_size, seq_len, hidden_size]`。
- 不要把 attention 矩阵理解成最终输出；它只是 token 之间的信息路由权重。
- 不要以为不同训练样本会在 attention 里互相看到；它们只通过共享参数的训练更新产生间接联系。
- 不要把 residual 理解成“把结果替换原始数据”；它是在原表示上叠加新信息。
- 不要把 FFN 理解成 token 之间交互；token 间交互主要发生在 attention。

## 复盘

Transformer 可以先理解成一个上下文加工器。Embedding 提供每个 token 的初始坐标，Transformer block 反复通过 attention 交换上下文信息，再通过 FFN 加工特征，最终得到可用于预测下一个 token 的 hidden states。

## 下一步

阅读 minGPT / nanoGPT 中 attention 模块的实现。
