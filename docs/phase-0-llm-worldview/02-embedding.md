---
layout: default
title: "Embedding"
---

# Embedding

## 学习状态

学习中。

## 当前理解

Embedding 可以理解为把 token 转成有语义关系的高维向量坐标。

完整链路：

```text
文本
-> tokenizer.encode
-> token ids
-> embedding lookup
-> token vectors
-> Transformer
```

Tokenizer 负责：

```text
文本 <-> token id
```

Embedding 层负责：

```text
token id -> dense vector
```

例如：

```text
"hello"
-> [15339]
-> embedding_matrix[15339]
-> [0.12, -0.08, 0.34, ...]
```

## 核心概念

- Token id 本身没有语义，需要通过 embedding 转成向量。
- 相似语义通常会在向量空间中距离更近。
- LLM 内部使用 token embedding，RAG 常用 text embedding。
- Embedding 是训练出来的，不是人工规则。
- Embedding matrix 的形状通常是 `[vocab_size, hidden_size]`。
- `hidden_size` 可以理解为每个 token 向量的维度，例如 4096 维。
- 单个维度通常不是人类可读的“高度、长度、颜色”等属性，而是模型训练出的内部坐标轴。
- 维度越高，模型容量通常越大，但计算、显存和训练数据需求也更高。

## 4096 维怎么理解？

4096 维可以类比成高维坐标空间：

```text
2 维：一个点用 [x, y] 表示
3 维：一个点用 [x, y, z] 表示
4096 维：一个 token 用 4096 个数表示
```

这个类比有帮助，但不能把每个维度简单理解成人类可命名的属性。真实模型里的某个维度通常不直接等于“高度”“颜色”“情绪”或“语法角色”。更准确地说，embedding 的多个维度组合起来表达 token 在训练语料中的统计关系、语义关系、语法关系和上下文倾向。

所以可以先用这个直觉：

```text
token id 是离散编号
embedding 是这个编号在连续高维空间里的坐标
训练过程让这些坐标逐渐变得对预测任务有用
```

## Embedding matrix 是什么？

Embedding 层维护一个二维矩阵：

```text
embedding_matrix shape = [vocab_size, hidden_size]
```

例如：

```text
vocab_size = 50000
hidden_size = 4096

embedding_matrix = 50000 行 x 4096 列
```

含义是：

```text
每一行 = 一个 token id 对应的向量
每一列 = 向量中的一个维度
```

这里更适合先类比成一张表格或数据库表，而不是二维语义空间：

```text
embedding_matrix ≈ 一张数据库表

行 = token 记录
列 = embedding 维度字段
单元格 = 这个 token 在这个维度上的数值
整行 = 这个 token 的完整 embedding 向量
```

例如：

| token_id | dim_0 | dim_1 | dim_2 | ... | dim_4095 |
| --- | --- | --- | --- | --- | --- |
| 123 | 0.12 | -0.08 | 0.34 | ... | 0.91 |
| 456 | -0.21 | 0.44 | 0.03 | ... | -0.17 |

所以：

```python
embedding_matrix[123]
```

拿到的不是某个单元格，而是 token 123 的整行：

```python
[0.12, -0.08, 0.34, ..., 0.91]
```

这整行才是 token 123 在 4096 维向量空间里的坐标。

因此需要区分三个概念：

```text
矩阵的 shape: [50000, 4096]
token 数量: 50000
向量空间维度: 4096
```

`[50000, 4096]` 不是“二维语义空间”，而是一张存放 50000 个 token 向量的二维表；每一行才是 4096 维空间里的一个点。

当输入 token ids 是：

```python
[10, 25, 100]
```

embedding lookup 本质上是查表：

```python
[
    embedding_matrix[10],
    embedding_matrix[25],
    embedding_matrix[100],
]
```

得到的结果形状是：

```text
[seq_len, hidden_size]
```

如果有 batch，则形状通常是：

```text
[batch_size, seq_len, hidden_size]
```

这里要区分：

```text
embedding matrix 本身是二维矩阵
一批输入查出来的 embedding 结果通常是三维张量
```

所以“矩阵一般是二维的”这个印象是对的；深度学习里经常还会用到更高维的数据结构，通常叫 tensor，中文叫张量。

## 为什么要 padding 成相同形状？

一批句子的 token 数通常不一样：

```text
句子 A：3 tokens
句子 B：7 tokens
句子 C：5 tokens
```

embedding 后分别是：

```text
[3, 4096]
[7, 4096]
[5, 4096]
```

这些长度不同的矩阵不能直接堆成一个规则 batch。GPU 和深度学习框架最擅长处理规则形状的大块数字数组，所以通常会把同一批样本 padding 到相同长度：

```text
句子 A：3 -> 7
句子 B：7 -> 7
句子 C：5 -> 7
```

得到：

```text
[batch_size, max_seq_len, hidden_size]
= [3, 7, 4096]
```

这个张量就是 Transformer 的输入表示之一。它会继续经过：

```text
embedding tensor
-> attention
-> feed-forward network
-> 多层 Transformer block
-> logits
-> 下一个 token 概率
```

常见形状变化：

```text
token ids
[batch_size, seq_len]

-> embedding
[batch_size, seq_len, hidden_size]

-> Transformer
[batch_size, seq_len, hidden_size]

-> LM head / output projection
[batch_size, seq_len, vocab_size]
```

Padding 的目的不是增加语义，而是方便并行计算。填充值本身不应该影响模型结果，所以还会配合 attention mask：

```text
1 = 真实 token
0 = padding token
```

模型通过 attention mask 知道哪些位置是真实内容，哪些位置只是补齐用的 `<pad>`。理想情况下，padding 位置不会作为真实语义参与 attention 和 loss 计算。

## Embedding 是如何学出来的？

Tokenizer/vocab 只定义：

```text
token -> token id
```

例如：

```text
"cat" -> 123
"dog" -> 456
```

这些 id 本身没有语义。Embedding matrix 一开始通常随机初始化，真正让向量变得有用的是语言模型训练：

```text
token ids 输入模型
-> 查 embedding 表得到向量
-> 模型预测下一个 token
-> 根据预测错误反向传播
-> 更新 Transformer 参数
-> 同时更新 embedding 向量
```

更准确地说：

```text
embedding lookup：把 token id 查表变成向量
embedding training：通过语言模型训练，让这些向量逐渐有用
```

不要理解成 vocab 一生成，embedding 空间就自然有语义。语义关系是在训练过程中被塑造出来的。

前向计算时，embedding 层本身只是查表：

```text
token id
-> embedding_matrix[token_id]
-> token vector
```

它不是在这一刻现场“理解语义”。语义是在训练循环中逐步写入 embedding matrix 的：

```text
文本
-> tokenizer
-> token ids
-> embedding lookup
-> token vectors
-> Transformer 结合上下文重新加工
-> hidden states
-> LM head
-> logits
-> 预测下一个 token
-> loss
-> 反向传播更新 embedding + Transformer 参数
```

例如 `cat` 和 `dog` 经常出现在类似上下文里：

```text
The cat eats ...
The dog eats ...
I have a cat
I have a dog
```

模型不是被人工告知 `cat` 和 `dog` 都是动物，而是在大量预测任务里发现它们在上下文中的行为相似。为了降低预测错误，训练会逐步调整相关参数，包括 `cat`、`dog` 对应的 embedding 行向量。

还要区分：

```text
embedding vector：某个 token 的初始静态表示
hidden state：这个 token 在当前上下文中的动态表示
```

例如同一个 `bank`：

```text
river bank
bank account
```

Embedding lookup 查出的 `bank` 初始向量是一样的；进入 Transformer 后，因为上下文不同，它的 hidden state 会变成不同的上下文表示。

所以：

```text
Embedding 层提供 token 的基础坐标
Transformer 根据上下文把基础坐标加工成上下文语义
训练过程把这种能力写进 embedding 和 Transformer 参数里
```

## 待学习问题

- Token embedding 和 text embedding 有什么区别？
- Embedding 维度代表什么？
- 为什么向量相似度可以用于语义检索？
- cosine similarity、dot product、L2 distance 的使用场景是什么？
- 矩阵、向量、张量在模型输入输出里分别对应什么？
- embedding matrix 和 Transformer 内部 hidden states 有什么关系？
- 反向传播如何知道应该更新哪些参数、往哪个方向更新？

## 实践记录

### 2026-05-18：Embedding 基础概念

本轮完成的理解：

- Embedding 不是 tokenizer 做的；tokenizer 只负责文本和 token id 的转换。
- Embedding 层负责把 token id 转成向量。
- 4096 维可以理解为一个 4096 维高维坐标，但单个维度通常不可读。
- Embedding matrix 本身是二维矩阵，形状是 `[vocab_size, hidden_size]`。
- Embedding matrix 更像数据库表：每行是一个 token，每列是一个 embedding 维度。
- `[50000, 4096]` 不是二维语义空间，而是 50000 个 token 向量，每个向量有 4096 维。
- 输入序列查表后的结果是 `[seq_len, hidden_size]`。
- 带 batch 时，结果通常是 `[batch_size, seq_len, hidden_size]`，这是三维张量。
- 不同长度的句子会 padding 到同一个 `max_seq_len`，得到规则张量，方便 GPU 并行计算。
- Padding 填充值本身不应该影响结果，需要通过 attention mask 和 loss mask 屏蔽。
- Embedding 向量通常随机初始化，然后随着语言模型训练被更新。
- 前向计算时 embedding 只是查表；语义是在训练中通过 loss 和反向传播逐步写入 embedding matrix 的。
- Embedding vector 是 token 的静态初始表示，Transformer hidden state 是结合上下文后的动态表示。

练习代码段：

```python
token_ids = tokenizer.encode("hello world")

vectors = embedding_matrix[token_ids]

output = transformer(vectors)
```

## 关键代码

```python
embedding_matrix.shape == (vocab_size, hidden_size)
token_vector = embedding_matrix[token_id]
sequence_vectors = embedding_matrix[token_ids]
```

## 踩坑

- 不要把 token id 本身理解成语义；id 只是词表编号。
- 不要把 embedding 的每一维强行解释成人类可命名属性；通常是模型内部学出来的混合特征。
- 不要把 embedding matrix 的二维 shape 误解成二维语义空间；它是二维表，向量空间维度由列数 `hidden_size` 决定。
- 不要把一个 token 对应到某个单元格；一个 token 对应的是 embedding matrix 里的一整行。
- 不要把 embedding matrix 和一次输入得到的 embedding tensor 混在一起：前者通常二维，后者带 batch 时通常三维。
- 不要以为 padding 是语义内容；它只是为了把不等长样本拼成规则张量，必须被 mask 掉。
- 不要把 embedding lookup 理解成现场语义推理；它只是取出已经训练好的向量。
- 不要把 embedding vector 和 hidden state 混为一谈；前者不看上下文，后者强依赖上下文。

## 复盘

Embedding 是 tokenizer 和 Transformer 之间的桥。Tokenizer 把文本变成离散 id，embedding 把离散 id 变成连续向量，Transformer 后续所有计算都建立在这些向量表示上。

## 下一步

用一个 embedding 模型计算几组文本向量，观察相似度。
