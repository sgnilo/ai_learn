---
layout: default
title: "LM Head、Logits、Loss 与训练循环"
---

# LM Head、Logits、Loss 与训练循环

## 学习状态

开始学习。

## 当前理解

Transformer 输出的是每个 token 的 hidden state，但训练和生成最终需要的是“下一个 token 是谁”。

因此还需要一段从 hidden state 到训练信号的链路：

```text
hidden_states
-> LM head
-> logits
-> softmax probabilities
-> next-token label
-> cross entropy loss
-> backpropagation
-> optimizer update
```

这一章连接的是：

```text
模型前向计算
-> 错误有多大
-> 参数如何被更新
```

它是从“模型结构”进入“模型为什么能学会”的关键桥梁。

## 核心概念

- LM Head
- Logits
- Softmax
- Next-token prediction
- Label shifting
- Cross entropy loss
- Backpropagation
- Gradient
- Optimizer
- Training loop

## 主流程

假设 Transformer 最后一层输出：

```text
hidden_states: [batch_size, seq_len, hidden_size]
```

LM head 会把每个位置的 hidden vector 映射到词表空间：

```text
LM head: [hidden_size, vocab_size]

logits = hidden_states @ LM_head
logits: [batch_size, seq_len, vocab_size]
```

其中：

```text
logits[b][t] = 第 b 个样本、第 t 个位置对整个 vocab 的未归一化分数
```

训练时，decoder-only LLM 通常做 next-token prediction：

```text
输入 token ids:
[t0, t1, t2, t3]

模型在各位置预测:
位置 0 预测 t1
位置 1 预测 t2
位置 2 预测 t3
```

所以 label 会相对输入右移一位：

```text
input:  [t0, t1, t2]
label:  [t1, t2, t3]
```

模型输出 logits 后，用 cross entropy 比较：

```text
模型认为每个 token 的概率分布
vs
真实下一个 token
```

loss 越小，说明模型越接近真实下一个 token。

## 待学习问题

- LM head 为什么把 hidden_size 映射到 vocab_size？
- logits 和 probability 有什么区别？
- softmax 为什么能把 logits 变成概率分布？
- next-token prediction 的 label 为什么要 shift？
- cross entropy loss 到底在惩罚什么？
- 反向传播如何知道每个参数该往哪个方向改？
- gradient 和 optimizer 分别是什么？
- 一轮 training loop 包含哪些步骤？

## 实践记录

### 2026-05-21：章节顺序纠偏

本轮完成的理解：

- Transformer 后面不应该直接跳到 Context Window / KV Cache。
- 在学习推理性能之前，应先补齐 `hidden_states -> logits -> loss -> backpropagation -> optimizer update` 这条训练主链路。
- Context Window / KV Cache 更偏推理成本和服务优化，应该在理解训练闭环之后学习。

练习代码段：

```text
token ids
-> embedding
-> Transformer
-> hidden_states
-> LM head
-> logits
-> cross entropy loss
-> backpropagation
-> optimizer.step()
```

### 2026-05-21：训练主链路总览

本轮完成的理解：

- Transformer 负责把上下文加工成 `hidden_states`。
- LM head 把 `hidden_states` 映射到词表空间，得到每个位置对所有 token 的候选分数。
- Logits 是 softmax 前的未归一化分数，不是概率。
- Softmax 把 logits 转成概率分布。
- Label 是真实的下一个 token，通常由原 token 序列右移一位得到。
- Cross entropy loss 衡量模型给真实下一个 token 的概率够不够高。
- Backpropagation 根据 loss 计算每个参数对错误的贡献和修改方向。
- Optimizer 根据梯度真正更新 embedding、Transformer、LM head 等参数。

训练 step 可以压缩成：

```text
1. 取一批 token ids
2. 构造 input ids 和 labels
3. forward: embedding -> Transformer -> LM head -> logits
4. loss: logits vs labels
5. backward: loss 反向传播得到 gradients
6. optimizer.step(): 更新参数
7. optimizer.zero_grad(): 清空梯度，进入下一批
```

本轮关键心智模型：

```text
模型怎么计算：token ids -> hidden_states -> logits
模型怎么知道错：logits -> probabilities -> loss
模型怎么学习：loss -> gradients -> optimizer update
```

### 2026-05-21：LM Head coding 练习

本轮搭好的练习入口：

- 源码入口：`practice/src/ai_practice/lm_head.py`
- 测试入口：`practice/tests/test_lm_head.py`
- 当前状态：测试已写好，源码函数暂时抛出 `NotImplementedError`，用于 TDD 红灯练习。

练习目标：

```text
hidden_states: [seq_len, hidden_size]
lm_head:       [hidden_size, vocab_size]
logits:        [seq_len, vocab_size]
```

待实现函数：

```python
def lm_head_logits(
    hidden_states: list[list[float]],
    lm_head: list[list[float]],
) -> list[list[float]]:
    ...
```

验证命令：

```bash
PYTHONPATH=practice/src python3 -m unittest practice.tests.test_lm_head
```

### 2026-05-21：LM Head coding 练习完成

本轮完成的实现：

- `lm_head_logits` 手写完成 `hidden_states @ lm_head`。
- 输入 `hidden_states` 的 shape 是 `[seq_len, hidden_size]`。
- 参数 `lm_head` 的 shape 是 `[hidden_size, vocab_size]`。
- 输出 `logits` 的 shape 是 `[seq_len, vocab_size]`。
- 每个 token 位置都会得到一整行 vocab logits。

完成版代码段：

```python
def lm_head_logits(hidden_states, lm_head):
    vocab_size = len(lm_head[0])
    logits = [[0.0 for _ in range(vocab_size)] for _ in hidden_states]

    for token_index, hidden_vector in enumerate(hidden_states):
        for vocab_index in range(vocab_size):
            for hidden_index, hidden_value in enumerate(hidden_vector):
                logits[token_index][vocab_index] += (
                    hidden_value * lm_head[hidden_index][vocab_index]
                )

    return logits
```

本轮踩坑：

- `lm_head` 没有 token 维度，不能用 token index 去访问 `lm_head[token_index]`。
- 输出的行数来自 `seq_len`，输出的列数来自 `vocab_size`。
- 中间被求和掉的是 `hidden_size` 维度。

验证命令：

```bash
PYTHONPATH=practice/src python3 -m unittest discover -s practice/tests
```

### 2026-05-21：Logits Softmax coding 练习

本轮搭好的练习入口：

- 源码入口：`practice/src/ai_practice/softmax_logits.py`
- 测试入口：`practice/tests/test_softmax_logits.py`
- 当前状态：测试已写好，源码函数暂时抛出 `NotImplementedError`，用于 TDD 红灯练习。

练习目标：

```text
logits:        [vocab_size]
probabilities: [vocab_size]

logits_by_position: [seq_len, vocab_size]
probabilities:      [seq_len, vocab_size]
```

待实现函数：

```python
def softmax(logits: list[float]) -> list[float]:
    ...


def logits_to_probabilities(
    logits_by_position: list[list[float]],
) -> list[list[float]]:
    ...
```

关键点：

```text
每个位置的 vocab logits 单独做 softmax
不要把 [seq_len, vocab_size] 展平成一个大列表一起算
```

验证命令：

```bash
PYTHONPATH=practice/src python3 -m unittest practice.tests.test_softmax_logits
```

## 关键代码

```text
logits = hidden_states @ LM_head
probabilities = softmax(logits)
```

## 踩坑

- 不要把 logits 当成概率；logits 是 softmax 前的原始分数。
- 不要跳过 loss 和 backpropagation 就进入 KV Cache；否则只理解了推理结构，没有理解模型如何学习。

## 复盘

尚未复盘。

## 下一步

先理解 LM head 和 logits：为什么 Transformer 输出还要映射到 vocab_size，以及 logits 如何表示下一个 token 的候选分数。
