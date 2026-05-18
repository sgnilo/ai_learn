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
- Token id 是 tokenizer、embedding、Transformer 和输出层之间的统一索引。
- 相似语义通常会在向量空间中距离更近。
- LLM 内部使用 token embedding，RAG 常用 text embedding。
- Embedding 是训练出来的，不是人工规则。
- Embedding matrix 的形状通常是 `[vocab_size, hidden_size]`。
- `hidden_size` 可以理解为每个 token 向量的维度，例如 4096 维。
- 单个维度通常不是人类可读的“高度、长度、颜色”等属性，而是模型训练出的内部坐标轴。
- 维度越高，模型容量通常越大，但计算、显存和训练数据需求也更高。

## 为什么模型内部使用 token id？

Token 字符串主要用于 encode 和 decode：

```text
encode：文本 token -> token id
decode：token id -> 文本 token
```

一旦进入模型内部，系统主要使用 token id 和向量：

```text
文本
-> tokenizer encode
-> token ids
-> embedding lookup
-> Transformer
-> logits over vocab
-> 采样 token id
-> tokenizer decode
-> 文本
```

原因是：

- 模型只能做数值计算，字符串 token 不能直接参与矩阵乘法。
- `token_id` 可以高效索引 embedding matrix，例如 `embedding_matrix[token_id]`。
- 输出层 logits 的每个位置也对应一个 token id，例如 `logits[123]` 表示 token id 123 的分数。

因此 `vocab` 是共同协议：

```text
token string <-> token id
```

可以这样区分：

```text
token 字符串：给人看，负责文本边界
token id：给系统用，负责跨模块索引
embedding 向量：给模型算，负责数值表示
```

Token id 本身仍然没有语义，它只是索引。语义来自：

```text
token_id 对应的 embedding 行向量
+
Transformer 在上下文里的计算
+
训练过程中学到的参数
```

这也是为什么模型不能随便换 tokenizer。如果 token id 重新编号，embedding matrix 和输出层 logits 对应的含义都会错位。

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

## 训练和推理的主链路

可以把 LLM 的训练和推理拆成两条链路。

训练阶段：

```text
训练语料
-> tokenizer
-> token ids
-> embedding lookup
-> Transformer forward
-> 预测下一个 token
-> 和真实下一个 token 对比
-> 计算 loss
-> 反向传播
-> 更新 embedding matrix + Transformer 参数 + 输出层参数
-> 重复很多次
```

训练目标可以先理解为：

```text
让模型在大量上下文里更容易预测正确的下一个 token
```

训练结束后，固化下来的是一组模型权重：

```text
embedding matrix
Transformer layers
LM head / output projection
LayerNorm 等其他参数
```

推理阶段：

```text
用户输入
-> tokenizer
-> token ids
-> embedding lookup
-> Transformer forward
-> logits
-> 选择或采样下一个 token id
-> 把新 token id 追加到上下文
-> 再预测下一个 token
-> 循环直到停止
-> tokenizer.decode
-> 文本回答
```

关键区别：

```text
训练时：参数会被更新
推理时：参数固定，只做计算和采样
```

因此，普通聊天不会改变模型权重。除非额外做 fine-tuning、在线训练或外部记忆系统。

## 参数规模、数据质量和能力上限

Embedding 参数不等于数据质量。数据质量来自训练语料本身，训练数据会同时塑造 embedding matrix 和 Transformer 参数。

更准确地说：

```text
embedding 参数：影响 token 的基础表示能力
Transformer 参数：影响模型对上下文进行计算、组合、推理、预测的能力
数据质量：影响所有参数最终学成什么样
```

Embedding matrix 参数量：

```text
embedding_params = vocab_size * hidden_size
```

如果输出层 `LM head` 不和 embedding 共享权重，还会有：

```text
lm_head_params = hidden_size * vocab_size
```

Transformer 参数量主要来自每层里的 attention 和 MLP / FFN 大矩阵，粗略和这些因素相关：

```text
num_layers
hidden_size^2
intermediate_size
attention heads
```

因此：

```text
embedding 参数随 hidden_size 线性增长
Transformer 参数通常随 hidden_size 接近平方级增长，并且还乘以层数
```

这也是为什么模型越大，参数大头通常在 Transformer layers 里，而不是 embedding 表里。

常见关系：

```text
attention_heads * head_dim = hidden_size
intermediate_size ≈ 3x~5x hidden_size
```

模型规模越大，通常会同时增加：

```text
hidden_size
num_layers
attention heads
intermediate_size
```

更大的模型通常有更高能力上限：

```text
参数量更大
-> 表示容量更强
-> 能压缩和建模更多模式
-> 能处理更复杂关系
-> 通常能力更强、更全面
```

但这不是无条件成立。最终效果还取决于：

```text
数据质量
训练 token 数
训练策略
模型架构
后训练 / SFT / RLHF / DPO
推理策略
任务类型
```

所以更准确的判断是：

```text
在训练充分、数据足够好、架构合理的前提下，更大模型通常有更高能力上限。
```

工程上也不会总选最大模型，因为参数量越大，显存、延迟、吞吐、部署和 fine-tuning 成本也越高。实际选型要看任务复杂度和成本边界。

## 向量相似度：L2、Cosine、Dot Product

常见向量相似度 / 距离计算有三类：

```text
L2 distance：看两个点的直线距离
Cosine similarity：看两个向量方向是否接近
Dot product：看方向和长度的综合相似度
```

L2 距离：

```text
distance(a, b) = sqrt(sum((a_i - b_i)^2))
```

距离越小越相似。二维直觉：

```text
A = [1, 2]
B = [4, 6]
distance = sqrt((1-4)^2 + (2-6)^2) = 5
```

Cosine similarity：

```text
cosine(a, b) = dot(a, b) / (norm(a) * norm(b))
```

越接近 1，方向越相似。

Dot product：

```text
dot(a, b) = sum(a_i * b_i)
```

分数越大越相似，但它同时受到方向和向量长度影响。

从几何上看，向量不只是一个点，也可以理解成从原点出发的箭头。它同时有：

```text
方向
长度
```

Cosine similarity 看的是两个向量的夹角：

```text
夹角 0°：方向完全一样，cosine = 1
夹角 90°：方向无关，cosine = 0
夹角 180°：方向相反，cosine = -1
```

所以：

```text
cosine 越大
-> 夹角越小
-> 方向越接近
-> 语义越可能相似
```

Dot product 可以理解成“一个向量在另一个向量方向上的投影有多强”：

```text
两个向量方向越一致，点积越大
两个向量越长，点积也越大
两个向量垂直，点积为 0
方向相反，点积为负
```

它们的关系是：

```text
a · b = |a| * |b| * cos(theta)
```

Cosine similarity 就是把长度影响除掉：

```text
cos(theta) = (a · b) / (|a| * |b|)
```

因此可以这样记：

```text
dot product：方向相似度 + 长度影响
cosine similarity：去掉长度影响，只看方向相似度
```

为什么 text embedding 常用 cosine / normalized dot product？

很多语义 embedding 更希望比较“方向”是否接近，而不是绝对长度是否接近。例如：

```text
A = [1, 1]
B = [10, 10]
C = [1, -1]
```

`A` 和 `B` 方向完全一样：

```text
cos(A, B) = 1
```

但 L2 距离很远：

```text
distance(A, B) ≈ 12.7
```

`A` 和 `C` 的 L2 更近：

```text
distance(A, C) = 2
```

但方向差异明显：

```text
cos(A, C) = 0
```

所以如果语义主要编码在方向里，L2 可能会被向量长度干扰。

生产里常见做法：

```text
先把 embedding 归一化成单位向量
再用 dot product / inner product 检索
```

归一化后：

```text
norm(a) = 1
norm(b) = 1
cosine(a, b) = dot(a, b)
```

这在语义上等价于 cosine，在工程上更容易用矩阵乘法和向量数据库加速。

L2 不是不能用。适合的情况包括：

```text
向量长度本身有意义
模型就是按 L2 距离训练的
向量已经归一化，此时 L2 排序和 cosine 排序一致
聚类或几何距离任务
```

归一化向量下：

```text
L2^2 = ||a - b||^2
     = ||a||^2 + ||b||^2 - 2a·b
     = 2 - 2cos(a, b)
```

因此：

```text
cosine 越大
L2 越小
```

排序关系一致。

## 已厘清问题

- Embedding 维度代表什么：`hidden_size` 是每个 token 向量的长度，不是二维矩阵的空间维度。
- Embedding matrix 是什么：它是 `[vocab_size, hidden_size]` 的二维表，每行是一个 token 的完整向量。
- 矩阵、向量、张量在这里怎么对应：一个 token 是向量，一句话是 `[seq_len, hidden_size]`，一批句子是 `[batch_size, seq_len, hidden_size]`。
- 为什么要 padding：为了把不等长样本拼成规则张量，方便 GPU 并行计算；padding 本身需要被 mask 掉。
- Embedding vector 和 hidden state 的区别：前者是 token 的静态初始表示，后者是 Transformer 结合上下文后的动态表示。
- 语义如何融入 embedding：前向时只是查表，训练时通过 loss、反向传播和优化器逐步更新 embedding matrix。
- LLM 训练主链路：tokenized 数据反复预测下一个 token，通过 loss 更新 embedding、Transformer 和输出层参数。
- LLM 推理主链路：使用固定权重循环预测下一个 token，并追加回上下文，最后 decode 成文本。
- 参数规模和能力关系：模型越大通常能力上限越高，但前提是数据、训练、架构和后训练也跟得上。
- 向量相似度：L2 看位置距离，cosine 看方向，dot product 看方向和长度；text embedding 常用 cosine 或归一化点积。

## 待学习问题

- Token embedding 和 text embedding 有什么区别？
- 反向传播如何知道应该更新哪些参数、往哪个方向更新？
- loss、gradient、optimizer step 如何系统性串起来？
- position embedding / positional encoding 如何给 token 向量加入位置信息？
- autoregressive generation、sampling、temperature、top-p 如何影响生成结果？
- scaling law 如何描述参数量、数据量和训练计算量之间的关系？

## 实践记录

### 2026-05-18：Embedding 基础概念

本轮完成的理解：

- Embedding 不是 tokenizer 做的；tokenizer 只负责文本和 token id 的转换。
- Token id 是贯穿 tokenizer、embedding、Transformer、输出层和 decode 的统一索引。
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

### 2026-05-18：最小 embedding lookup 练习

本轮完成的理解：

- 纯 lookup 视角下，embedding 的实现就是多级索引。
- 一个 token id 索引 embedding matrix 的一整行，得到 `[hidden_size]`。
- 一句话是一组 token id，逐个查表后得到 `[seq_len, hidden_size]`。
- 一个 batch 是多句话，逐句查表后得到 `[batch_size, seq_len, hidden_size]`。
- 这个练习的关键不是算法复杂度，而是区分矩阵 shape、向量维度、序列长度和 batch 维度。

练习代码段：

```python
class SimpleEmbedding:
    def __init__(self, embedding_matrix: list[list[float]]) -> None:
        self._embedding_matrix = embedding_matrix

    def lookup_one(self, token_id: int) -> list[float]:
        if token_id < 0:
            raise ValueError(f"invalid token id: {token_id}")

        try:
            return self._embedding_matrix[token_id]
        except IndexError:
            raise ValueError(f"invalid token id: {token_id}") from None

    def lookup_sequence(self, token_ids: list[int]) -> list[list[float]]:
        return [self.lookup_one(token_id) for token_id in token_ids]

    def lookup_batch(self, batch_token_ids: list[list[int]]) -> list[list[list[float]]]:
        return [self.lookup_sequence(token_ids) for token_ids in batch_token_ids]
```

练习测试段：

```python
def test_lookup_batch_returns_batch_by_seq_len_by_hidden_size(self) -> None:
    self.assertEqual(
        self.embedding.lookup_batch([[0, 2], [1, 0]]),
        [
            [[0.1, 0.2], [0.5, 0.6]],
            [[0.3, 0.4], [0.1, 0.2]],
        ],
    )
```

验证：

```text
PYTHONPATH=src python3 -m unittest discover -s tests
Ran 8 tests in 0.000s
OK
```

### 2026-05-18：训练和推理主链路

本轮完成的理解：

- 模型训练不是只训练 embedding，而是同时更新 embedding matrix、Transformer block、输出层等参数。
- 训练 loop 可以理解为：预测下一个 token、计算 loss、反向传播、优化参数、重复很多次。
- 推理时参数固定，不再更新，只使用训练好的权重做前向计算。
- 生成式 LLM 通常一次预测一个 token，把新 token 追加回上下文，再继续预测下一个 token。

练习代码段：

```text
training:
tokens -> embedding -> transformer -> logits -> loss -> backprop -> update weights

inference:
prompt tokens -> embedding -> transformer -> logits -> sample next token -> append -> repeat -> decode
```

### 2026-05-18：参数规模和能力上限

本轮完成的理解：

- 几十亿、几百亿参数指的是模型所有可训练权重总数，包括 embedding、Transformer、输出层等。
- Embedding 参数负责 token 的基础坐标表，不直接代表数据质量。
- Transformer 参数负责上下文计算、组合、推理和预测，是大模型参数量的主要来源。
- 数据质量会同时影响 embedding 和 Transformer 参数学成什么样。
- 在训练充分、数据好、架构合理的前提下，更大模型通常能力上限更高。
- 工程上还要考虑显存、延迟、吞吐和成本，不是所有任务都应该选最大模型。

练习代码段：

```text
embedding_params = vocab_size * hidden_size
lm_head_params = hidden_size * vocab_size
transformer_params ≈ num_layers * hidden_size^2 * constants
```

### 2026-05-18：向量相似度选择

本轮完成的理解：

- L2、cosine、dot product 都可以衡量向量相近，但含义不同。
- L2 看两个点的绝对距离，不一定等于语义更接近。
- Cosine 更关注方向，适合很多 text embedding 的语义相似度。
- Dot product 在未归一化时同时受方向和长度影响。
- 向量归一化后，dot product 等价于 cosine，L2 排序也和 cosine 单调对应。
- 生产检索常用 normalized embedding + dot product，是语义和工程效率的折中。

练习代码段：

```python
dot = sum(a * b for a, b in zip(left, right))
left_norm = sqrt(sum(a * a for a in left))
right_norm = sqrt(sum(b * b for b in right))
score = dot / (left_norm * right_norm)
```

### 2026-05-19：Text embedding 相似度练习

实践目录：

- 代码：`practice/src/ai_practice/text_embedding.py`
- 测试：`practice/tests/test_text_embedding.py`
- 测试数据：`practice/tests/fixtures/text_embedding_cases.json`

本轮完成的理解：

- text embedding 相似度练习可以先把“模型产出向量”和“相似度计算/排序逻辑”拆开。
- `EmbeddingModel` 只需要提供 `embed_texts(texts) -> vectors` 接口。
- `cosine_similarity` 负责比较两个向量方向是否接近。
- `TextEmbeddingSimilarity.score` 负责把两段文本转成向量并计算相似度。
- `TextEmbeddingSimilarity.rank` 负责对候选文本按相似度从高到低排序。
- 测试中用 deterministic fake embedding model，避免依赖网络下载真实模型；后续可以替换成真实 embedding backend。

练习代码段：

```python
from dataclasses import dataclass
import math


@dataclass
class RankedText:
    text: str
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("same dimensions")

    left_norm = math.sqrt(sum(x * x for x in left))
    right_norm = math.sqrt(sum(x * x for x in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    dot = sum(a * b for a, b in zip(left, right))
    return dot / (left_norm * right_norm)


class TextEmbeddingSimilarity:
    def __init__(self, embedding_model) -> None:
        self._embedding_model = embedding_model

    def score(self, left_text: str, right_text: str) -> float:
        vectors = self._embedding_model.embed_texts([left_text, right_text])
        return cosine_similarity(vectors[0], vectors[1])

    def rank(self, query: str, candidates: list[str]):
        scores = [RankedText(candidate, self.score(query, candidate)) for candidate in candidates]
        return sorted(scores, key=lambda x: x.score, reverse=True)
```

练习测试段：

```python
def test_positive_text_scores_higher_than_negative_text(self) -> None:
    for case in self.cases:
        with self.subTest(case=case["id"]):
            positive_score = self.similarity.score(case["query"], case["positive"])
            negative_score = self.similarity.score(case["query"], case["negative"])

            self.assertGreater(positive_score, negative_score)


def test_rank_returns_most_similar_text_first(self) -> None:
    case = self.cases[0]

    ranked = self.similarity.rank(
        case["query"],
        [
            case["negative"],
            case["positive"],
        ],
    )

    self.assertEqual(ranked[0].text, case["positive"])
    self.assertGreater(ranked[0].score, ranked[1].score)
```

验证：

```text
PYTHONPATH=src python3 -m unittest discover -s tests
Ran 12 tests in 0.001s
OK
```

## 关键代码

```python
embedding_matrix.shape == (vocab_size, hidden_size)
token_vector = embedding_matrix[token_id]
sequence_vectors = embedding_matrix[token_ids]
batch_vectors = [embedding_matrix[token_ids] for token_ids in batch_token_ids]
text_score = cosine_similarity(query_embedding, candidate_embedding)
```

## 踩坑

- 不要把 token id 本身理解成语义；id 只是词表编号。
- 不要把 token 字符串带入模型内部计算；模型内部需要的是 token id 和向量。
- 不要把 embedding 的每一维强行解释成人类可命名属性；通常是模型内部学出来的混合特征。
- 不要把 embedding matrix 的二维 shape 误解成二维语义空间；它是二维表，向量空间维度由列数 `hidden_size` 决定。
- 不要把一个 token 对应到某个单元格；一个 token 对应的是 embedding matrix 里的一整行。
- 不要把 embedding matrix 和一次输入得到的 embedding tensor 混在一起：前者通常二维，后者带 batch 时通常三维。
- 不要以为 padding 是语义内容；它只是为了把不等长样本拼成规则张量，必须被 mask 掉。
- 不要把 embedding lookup 理解成现场语义推理；它只是取出已经训练好的向量。
- 不要把 embedding vector 和 hidden state 混为一谈；前者不看上下文，后者强依赖上下文。
- 不要把 lookup 练习想复杂；它的本质是按 token id 对 embedding matrix 做一层、两层、三层索引。
- 不要以为推理阶段会继续修改模型权重；普通推理只使用固定参数做前向计算和采样。
- 不要把 embedding 参数理解成数据质量；数据质量来自训练语料，并影响所有参数。
- 不要把“模型更大通常更强”理解成绝对规律；训练不足或数据差的大模型可能不如训练好的小模型。
- 不要默认 L2 更精准；如果语义主要编码在向量方向里，L2 可能被向量长度干扰。
- 不要把真实 embedding backend 和相似度排序逻辑绑死；先用固定 fake vectors 验证排序规则更清晰。

## 复盘

Embedding 是 tokenizer 和 Transformer 之间的桥。Tokenizer 把文本变成离散 id，embedding 把离散 id 变成连续向量，Transformer 后续所有计算都建立在这些向量表示上。

这一章目前已经串起了：

```text
token id
-> embedding lookup
-> batch tensor
-> Transformer 输入
-> 训练时更新参数
-> 推理时固定参数逐 token 生成
```

## 下一步

1. 接入一个真实 embedding 模型，替换 fake embedding backend，观察同一批测试文本的相似度。
2. 后续在训练章节系统学习 loss、gradient、backprop、optimizer。
