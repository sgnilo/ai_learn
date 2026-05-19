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
- Causal Mask
- Decoder-only LLM
- Positional Encoding / Position Embedding
- Feed Forward Network
- Residual Connection
- LayerNorm

## Transformer block 的主流程

一个简化的 Transformer block 可以理解为：

```text
输入 hidden states
-> LayerNorm / RMSNorm
-> Self-Attention
-> 残差连接：x = x + attention_delta
-> LayerNorm / RMSNorm
-> Feed Forward Network
-> 残差连接：x = x + ffn_delta
-> 输出 hidden states
```

直觉上：

```text
Attention：横向看上下文，token 与 token 交互
FFN / MLP：纵向加工特征，增强每个 token 自己的表达能力
Residual：保留原始信息，并叠加新信息
Norm：稳定数值尺度，让深层训练更稳定
```

现代很多 LLM 采用 pre-norm 结构，也就是先 norm，再进入 attention / FFN：

```text
x = x + Attention(Norm(x))
x = x + FFN(Norm(x))
```

因此，Norm 更准确的角色是稳定送入子层的输入尺度，而不是在 attention / FFN 之后专门去规范化 delta。Attention / FFN 负责计算变化量，Residual 负责把变化量叠加回 hidden states。

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

如果序列长度是 4，允许看到的位置是一个下三角矩阵：

```text
        看谁
        0   1   2   3
当前 0  ✓   x   x   x
当前 1  ✓   ✓   x   x
当前 2  ✓   ✓   ✓   x
当前 3  ✓   ✓   ✓   ✓
```

实际做法通常是在 softmax 之前处理 attention score：

```text
scores = Q @ K^T / sqrt(d_k)
scores[未来位置] = -inf
weights = softmax(scores)
out = weights @ V
```

因为 `softmax(-inf) = 0`，所以未来位置的 attention 权重会变成 0，不参与后面对 `V` 的加权求和。

伪代码：

```python
scores = Q @ K.T / math.sqrt(d_k)
mask = lower_triangular_matrix(seq_len)
scores = scores.masked_fill(mask == 0, -float("inf"))
weights = softmax(scores)
out = weights @ V
```

## Decoder-only LLM

Decoder-only LLM 指只使用 Transformer 的 decoder 风格结构，并通过自回归方式生成文本：

```text
给定前面的 token，预测下一个 token
把预测结果拼回上下文
继续预测下一个 token
```

例如：

```text
输入：今天天气
预测：很
输入：今天天气很
预测：好
```

这里的核心约束就是 causal mask：当前位置只能看自己和之前的 token，不能看未来 token。

基本流程：

```text
tokens
-> embedding
-> 多层 decoder Transformer block
   -> masked self-attention / causal self-attention
   -> FFN
-> logits
-> 预测下一个 token
```

和其他 Transformer 架构的区别：

```text
Encoder-only：双向看完整输入，适合理解、分类、检索，不天然适合长文本自回归生成
Encoder-decoder：encoder 读输入，decoder 生成输出，常见于翻译、摘要、text-to-text
Decoder-only：只用 decoder 风格堆叠，通过 causal mask 从左到右预测下一个 token
```

当前主流聊天和生成式 LLM 大多走 decoder-only 路线，例如 GPT、LLaMA、Mistral、Qwen、DeepSeek 等。

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

更细地看，一个普通 FFN 可以写成：

```text
h = x @ W_up + b_up
h = activation(h)
out = h @ W_down + b_down
```

对应 shape：

```text
x: [hidden_size]
W_up: [hidden_size, intermediate_size]
h: [intermediate_size]
W_down: [intermediate_size, hidden_size]
out: [hidden_size]
```

如果带 batch 和 seq_len：

```text
x: [batch_size, seq_len, hidden_size]
W_up: [hidden_size, intermediate_size]
h: [batch_size, seq_len, intermediate_size]
out: [batch_size, seq_len, hidden_size]
```

### 升维是怎么来的？

升维不是枚举原特征之间的排列组合，而是通过一个可训练权重矩阵，把原 hidden vector 投影到更多中间特征通道。

例如从 3 维升到 4 维：

```text
x = [x1, x2, x3]
W_up shape = [3, 4]
```

矩阵可以写成：

```text
        h1   h2   h3   h4
      ┌                    ┐
x1 -> │ w11  w12  w13  w14 │
x2 -> │ w21  w22  w23  w24 │
x3 -> │ w31  w32  w33  w34 │
      └                    ┘
```

计算：

```text
h1 = x1*w11 + x2*w21 + x3*w31
h2 = x1*w12 + x2*w22 + x3*w32
h3 = x1*w13 + x2*w23 + x3*w33
h4 = x1*w14 + x2*w24 + x3*w34
```

因此，第 4 个新维度不是凭空来的，也不是 `x1` 和某个 `x4` 的组合。它由第 4 列权重定义：

```text
h4 = x1*w14 + x2*w24 + x3*w34
```

也就是说：

```text
W_up 的每一列 = 一组可训练权重 = 一个中间特征探测器
```

如果升到 5 维，就多一列：

```text
h5 = x1*w15 + x2*w25 + x3*w35
```

这些权重一开始通常随机初始化，训练时通过 loss 和反向传播更新。升维给模型更多“临时特征槽位”，让它可以学习更多组不同的加权组合特征。

### Activation 是什么？

如果只有线性层：

```text
Linear(Linear(Linear(x)))
```

整体仍然等价于一个大的线性变换，表达能力有限。Activation function 的作用是在两个线性层之间加入非线性。

常见 activation：

```text
ReLU(x) = max(0, x)
SiLU(x) = x * sigmoid(x)
GELU：更平滑的 ReLU 风格激活
```

### SiLU 如何做非线性加工？

SiLU 也叫 Swish，公式是：

```text
SiLU(x) = x * sigmoid(x)
sigmoid(x) = 1 / (1 + e^(-x))
```

它可以拆成两步看：

```text
gate = sigmoid(x)
out = x * gate
```

`sigmoid(x)` 会把任意输入压到 `0 ~ 1` 之间：

```text
x 很大为正 -> sigmoid(x) 接近 1
x 接近 0   -> sigmoid(x) 接近 0.5
x 很大为负 -> sigmoid(x) 接近 0
```

所以 SiLU 的直觉是：先根据 `x` 自己算一个软门控比例，再用这个比例乘回 `x`。

例如：

```text
x =  3.0 -> sigmoid(x) ≈ 0.95 -> SiLU(x) ≈  2.86
x =  0.0 -> sigmoid(x) =  0.50 -> SiLU(x) =   0.0
x = -1.0 -> sigmoid(x) ≈ 0.27 -> SiLU(x) ≈ -0.27
x = -5.0 -> sigmoid(x) ≈ 0.01 -> SiLU(x) ≈ -0.03
```

这和 ReLU 的区别是：

```text
ReLU：负数直接砍成 0，正数原样通过
SiLU：负数被平滑压低，正数被逐渐放行
```

因此 SiLU 是一个平滑的非线性函数。它既保留了“正响应更容易通过”的倾向，又不会像 ReLU 一样在 0 点突然硬切。

直觉上，activation 像中间特征的阀门：

```text
ReLU：硬阀门，负数关掉，正数通过
GELU / SiLU：软阀门，不是硬切，而是平滑地压低或放行
SwiGLU：门控结构，一条分支产生候选特征，一条分支决定放行多少
```

Activation 通常作用在升维后的中间表示上：

```text
x -> W_up -> h: [intermediate_size]
h -> activation(h)
activation(h) -> W_down -> out: [hidden_size]
```

注意，activation 不直接有自然语言语义。它提供的是数值选择机制：某些中间特征响应被放行，某些被抑制。自然语言语义是训练后这些数值机制组合出来的效果。

### 为什么常见 activation 更偏向正响应？

ReLU、SiLU、GELU 这类 activation 通常都会让正响应更容易通过，让负响应被砍掉或压低。这里压低的是中间特征空间里的响应，不等于最终 FFN 只能做正向更新。

可以把 `W_up` 后的每个中间维度理解成一个特征探测器：

```text
h_i 很正：这个探测器被正向命中
h_i 接近 0：这个特征不明显
h_i 很负：更像反方向或不匹配
```

activation 的作用是让“正向命中”的中间特征更有资格参与后面的 `h @ W_down`，并抑制相关性不强或反向的中间响应。

但 `W_down` 的权重仍然可以是正数或负数：

```text
delta_j = h_i * W_down[i, j]
```

所以一个被正向激活的中间特征，最终既可以增强某些 hidden 维度，也可以削弱某些 hidden 维度。更准确地说：

```text
W_up + activation：选择哪些中间条件成立
W_down：决定这些条件成立后，如何更新原 hidden state
```

可以这样总结 FFN：

```text
升维：用更多组可训练权重生成中间特征响应
activation：对中间特征做非线性筛选和重编码
降维：把加工后的中间特征组合回 hidden_size
```

## Residual Connection 和 Norm

残差连接实现上通常就是同 shape hidden states 的逐元素加法：

```text
new_x = x + sublayer(x)
```

在现代 LLM 常见的 pre-norm 结构里，更接近：

```text
attention_delta = Attention(Norm(x))
x = x + attention_delta

ffn_delta = FFN(Norm(x))
x = x + ffn_delta
```

这里相加的是前向计算中的 hidden states / activation，不是模型参数。

如果：

```text
x.shape = [batch_size, seq_len, hidden_size]
attention_delta.shape = [batch_size, seq_len, hidden_size]
```

那么相加是逐元素发生的：

```text
new_x[b][t][h] = x[b][t][h] + attention_delta[b][t][h]
```

也就是说：

```text
batch 维度不变
token 位置不变
hidden_size 维度不变
每个 token 的 hidden vector 被加上一个修正量
```

之所以单独叫 residual connection，是因为它改变了子层的学习角色：

```text
没有残差：new_x = sublayer(x)
有残差：new_x = x + sublayer(x)
```

子层不必从零生成完整新表示，而是学习“相对原输入要改多少”。这个差值就是 residual / 残差。

Norm 的作用是把进入 attention / FFN 的 hidden vector 调到稳定尺度。

以 LayerNorm 的直觉版为例，它对每个 token 的 hidden vector 做归一化：

```text
x_i: [hidden_size]
mean = 平均值
variance = 方差
normalized = (x_i - mean) / sqrt(variance + eps)
output = normalized * gamma + beta
```

其中 `gamma` 和 `beta` 是可训练参数，用来让模型在稳定数值尺度后仍然可以学习合适的缩放和平移。

很多现代 LLM 使用 RMSNorm。它通常不减均值，而是按均方根缩放：

```text
rms = sqrt(mean(x_i^2) + eps)
output = x_i / rms * weight
```

可以先这样记：

```text
Residual：保留原表示，叠加子层学到的修正量
Norm：稳定每个 token 的 hidden vector 数值尺度
```

从高维空间看，Norm 的思想是：不要让每个 token 的 hidden vector 以任意尺度、任意偏移进入 attention / FFN，而是先把它拉回一个更稳定的数值范围。

以 LayerNorm 为例：

```text
x_i = [2, 4, 6]
mean = 4
std ≈ 1.63
normalized = (x_i - mean) / std ≈ [-1.22, 0, 1.22]
```

它做了两件事：

```text
中心化：减去均值，让整体偏移回到 0 附近
尺度化：除以标准差，让向量各维度的整体波动范围更稳定
```

然后再通过可训练参数恢复表达自由度：

```text
output = normalized * gamma + beta
```

可以理解为：

```text
先把输入放到稳定坐标系里
再允许模型学会需要的缩放和平移
```

这会让 attention / FFN 看到的输入分布更稳定，从而让它们输出的 `delta` 不容易因为输入尺度突然变大而爆掉。

如果没有 Norm，多层网络中每一层都会改变 hidden states 的数值分布：

```text
第 1 层输出稍微变大
-> 第 2 层基于更大的输入继续计算
-> 第 3 层可能更大
-> 深层后数值可能越来越不稳定
```

Norm 相当于在每个子层前做一次尺度校准：

```text
Norm(x)
-> Attention / FFN
-> delta
-> x + delta
```

它不能保证绝对不会出现极端值，但能显著降低数值尺度漂移，让训练更稳定、梯度更可控、深层堆叠更容易。

需要区分 Norm 和 Residual 的角色：

```text
Norm：稳定送入 attention / FFN 的输入尺度
Residual：把 attention / FFN 算出的 delta 加回原 hidden states
```

因此，Norm 不是在假设 delta 应该接近 0。`delta ≈ 0` 是 residual 结构下的一种可能学习结果：如果某层不需要大幅修改当前表示，子层可以学到输出很小的修正量。

LayerNorm 里的 `gamma` 和 `beta` 作用在 normalized hidden vector 上：

```text
output = normalized * gamma + beta
```

它们不是直接控制 residual 增量大小，而是控制送入 attention / FFN 之前的 normalized 表示如何按维度缩放和平移。

可以这样理解：

```text
Norm 先把 hidden vector 拉回稳定区域
gamma / beta 提供可训练的缩放和平移自由度
Attention / FFN 基于这个更稳定的输入计算 delta
Residual 再把 delta 加回原 hidden states
```

所以 `gamma / beta` 更像是 Norm 后恢复表达能力的可训练自由度，而不是对 delta 的直接开关。

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
- FFN 的升维是通过 `W_up: [hidden_size, intermediate_size]` 学出更多中间特征通道。
- Activation 作用在中间特征上，引入非线性选择机制。
- Residual 和 Norm 负责稳定信息传递和数值分布。
- Residual 操作的是 hidden states，不改变 batch、token 位置或 hidden_size 结构。
- Norm 通常对每个 token 的 hidden vector 做归一化，稳定进入 attention / FFN 的数值尺度。
- Norm 的高维直觉是把 hidden vector 拉回稳定尺度，再通过可训练缩放和平移保留表达能力。
- Norm 稳定的是子层输入；Residual 才是把子层输出的 delta 加回原 hidden states。
- 多层传递后，每个 token 的 hidden state 会逐步变成上下文相关表示。

练习代码段：

```text
x: [batch_size, seq_len, hidden_size]

x = x + Attention(Norm(x))
x = x + FFN(Norm(x))

output: [batch_size, seq_len, hidden_size]
```

### 2026-05-19：FFN 升维和 activation

本轮完成的理解：

- FFN 不是 token 间通信层，而是对每个 token 的 hidden vector 做非线性特征加工。
- 升维通过 `W_up` 完成，不是枚举特征组合，而是学习更多组加权组合通道。
- `W_up` 的每一列可以理解为一个中间特征探测器。
- 升维后的 `intermediate_size` 提供临时计算空间，不是最终输出维度。
- Activation 作用在升维后的中间特征上，引入非线性选择机制。
- ReLU / GELU / SiLU 可以先理解成不同风格的数值阀门。
- SiLU 的核心是 `x * sigmoid(x)`：用输入自己生成软门控比例，再乘回输入本身。
- activation 偏向采纳正向命中的中间特征，并抑制相关性不强的中间响应；最终是否增强或削弱原 hidden 维度由 `W_down` 决定。

练习代码段：

```text
x: [hidden_size]
W_up: [hidden_size, intermediate_size]
h = x @ W_up
h = activation(h)
out = h @ W_down
out: [hidden_size]
```

SiLU 数值例子：

```text
SiLU(3.0)  = 3.0  * sigmoid(3.0)  ≈  2.86
SiLU(-1.0) = -1.0 * sigmoid(-1.0) ≈ -0.27
SiLU(-5.0) = -5.0 * sigmoid(-5.0) ≈ -0.03
```

### 2026-05-19：Pre-Norm Transformer block 顺序

本轮完成的理解：

- 一个 Transformer block 的核心结构可以理解为两段：`Norm + Attention + Residual`，以及 `Norm + FFN + Residual`。
- 现代 LLM 常见写法是 `x = x + Attention(Norm(x))` 和 `x = x + FFN(Norm(x))`。
- Norm 稳定的是送入 attention / FFN 的 hidden states 尺度，不是专门把 attention / FFN 输出后的 delta 再做放缩平移。
- Attention 计算上下文变化量，FFN 计算特征加工变化量，Residual 把这些变化量叠加回原 hidden states。
- 一个 block 完成后输出同 shape 的新 hidden states，交给下一个 Transformer block。

练习代码段：

```text
x: [batch_size, seq_len, hidden_size]

attention_delta = SelfAttention(Norm(x))
x = x + attention_delta

ffn_delta = FFN(Norm(x))
x = x + ffn_delta

output: [batch_size, seq_len, hidden_size]
```

### 2026-05-19：多层 Transformer block 的工程实现

本轮完成的理解：

- 大模型通常堆叠很多层 Transformer block。
- 每一层 block 的计算逻辑基本相同，但每一层都有自己独立的可训练参数。
- 工程实现里通常定义一个 `TransformerBlock` 类，用它实例化出 `num_layers` 个 block。
- 类负责复用计算结构；实例负责持有真实参数。
- forward 时通过循环让 hidden states 依次经过这些 block。
- 如果只用同一个 block 实例反复调用，就是参数共享；主流 LLM 通常不是这样，而是共享代码结构、不共享每层参数。
- 在 PyTorch 里通常用 `ModuleList` 保存多个 block 实例，这样优化器才能发现并更新每层参数。

练习代码段：

```python
class TransformerBlock:
    def __init__(self):
        self.attn = SelfAttention()
        self.ffn = FeedForward()
        self.norm1 = RMSNorm()
        self.norm2 = RMSNorm()

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return x


class Transformer:
    def __init__(self, num_layers):
        self.layers = [
            TransformerBlock()
            for _ in range(num_layers)
        ]

    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x
```

对应真实框架里的思路：

```python
self.layers = nn.ModuleList([
    TransformerBlock(config)
    for _ in range(config.num_layers)
])
```

可以这样记：

```text
类：定义 block 的计算模板
实例：持有某一层自己的参数
循环：让 hidden states 逐层被 transform
```

### 2026-05-19：Causal Mask 和 Decoder-only LLM

本轮完成的理解：

- Decoder-only LLM 是当前主流生成式大模型常见架构路线。
- 它通过自回归方式工作：基于已有 token 预测下一个 token，再把预测 token 拼回上下文继续生成。
- Causal mask 是 decoder-only LLM 的核心约束：当前位置只能看自己和之前的 token，不能偷看未来 token。
- Causal mask 通常是下三角 mask，作用在 attention scores 上。
- 实现时会在 softmax 前把未来位置的 score 设成 `-inf`，让这些位置经过 softmax 后权重变成 0。
- Encoder-only 更偏理解任务；encoder-decoder 把输入理解和输出生成分成两套结构；decoder-only 用一套自回归生成结构同时承担理解和生成。

练习代码段：

```python
scores = Q @ K.T / math.sqrt(d_k)
mask = lower_triangular_matrix(seq_len)
scores = scores.masked_fill(mask == 0, -float("inf"))
weights = softmax(scores)
out = weights @ V
```

下三角直觉：

```text
当前 token i 只能 attend 到位置 <= i 的 token
未来位置 > i 的 attention weight = 0
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
- 不要忘记 decoder-only LLM 的 self-attention 通常带 causal mask；否则训练时会偷看未来 token。
- 不要把 decoder-only 理解成“只能解码不能理解”；它只是采用自回归 decoder 风格结构，仍然可以通过生成范式处理理解任务。
- 不要把 residual 理解成“把结果替换原始数据”；它是在原表示上叠加新信息。
- 不要把 residual 加法理解成参数相加；它加的是当前前向计算里的 hidden states / activation。
- 不要把 shape 写法神秘化；`[batch_size, seq_len, hidden_size]` 就是三层数组/张量三个轴上的长度。
- 不要把 `gamma / beta` 理解成直接控制 residual delta；它们控制的是 Norm 后表示的缩放和平移。
- 不要把现代 LLM 常见的 Pre-Norm 顺序理解反；通常是先 `Norm(x)`，再进入 attention / FFN，然后 residual 加回 `x`。
- 不要把多层 Transformer block 理解成同一个实例反复调用；主流实现通常是同一个类创建多个实例，每层参数独立。
- 不要把 FFN 理解成 token 之间交互；token 间交互主要发生在 attention。
- 不要把升维理解成已有维度的排列组合；它是通过可训练矩阵生成更多中间特征响应。
- 不要给 activation 强行绑定自然语言语义；它是数值层面的非线性筛选机制。
- 不要把 activation 压低负响应理解成“模型不做负向更新”；负向更新仍然可以通过 `W_down` 产生。

## 复盘

Transformer 可以先理解成一个上下文加工器。Embedding 提供每个 token 的初始坐标，Transformer block 反复通过 attention 交换上下文信息，再通过 FFN 加工特征，最终得到可用于预测下一个 token 的 hidden states。

## 下一步

阅读 minGPT / nanoGPT 或 Hugging Face 模型里的 causal self-attention 实现，对照 mask、scores、softmax 和 forward 循环。
