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

### 2026-05-21：Logits Softmax coding 练习完成

本轮完成的实现：

- `softmax` 将一行 vocab logits 转成概率分布。
- `logits_to_probabilities` 对 `[seq_len, vocab_size]` 的每一行分别做 softmax。
- 每个位置独立得到一个 vocab probability distribution。
- softmax 结果中每个概率都大于等于 0，并且每一行概率和为 1。

完成版代码段：

```python
def softmax(logits):
    exp_logits = [math.exp(logit) for logit in logits]
    exp_sum = sum(exp_logits)
    return [exp_logit / exp_sum for exp_logit in exp_logits]


def logits_to_probabilities(logits_by_position):
    return [softmax(logits) for logits in logits_by_position]
```

本轮踩坑：

- logits 是分数，不是概率；softmax 后才是概率分布。
- 对 `[seq_len, vocab_size]` 做 softmax 时，要按位置逐行计算，不能把所有位置展平成一个大列表。
- softmax 和 attention 中的 softmax 是同一种数学操作，但含义不同：attention 中表示“看哪些 token”，LM head 后表示“下一个 token 是谁”。

验证命令：

```bash
PYTHONPATH=practice/src python3 -m unittest discover -s practice/tests
```

### 2026-05-21：Next-token Loss coding 练习复盘

本轮练习入口：

- 源码入口：`practice/src/ai_practice/next_token_loss.py`
- 测试入口：`practice/tests/test_next_token_loss.py`
- 当前状态：实现已完成，目标测试通过。

练习目标：

```text
logits: [batch_size, seq_len, vocab_size]
labels: [batch_size, seq_len]

shift_logits = logits[:, :-1, :]
shift_labels = labels[:, 1:]
```

最终练习代码：

```python
from ai_practice.softmax_logits import softmax
import math


def shift_for_next_token_loss(
    logits: list[list[list[float]]],
    labels: list[list[int]],
) -> tuple[list[list[list[float]]], list[list[int]]]:
    shift_logits = []
    for i, logit in enumerate(logits):
        new_logit = []
        for j, _ in enumerate(logit):
            if j < len(logits[i]) - 1:
                new_logit.append(logits[i][j])
        shift_logits.append(new_logit)

    shift_labels = []
    for i, label in enumerate(labels):
        new_label = []
        for j, _ in enumerate(label):
            if j > 0:
                new_label.append(labels[i][j])
        shift_labels.append(new_label)

    return [shift_logits, shift_labels]


def negative_log_likelihood(
    probabilities: list[float],
    label: int,
) -> float:
    probability = probabilities[label]
    return -math.log(probability)


def shifted_cross_entropy_loss(
    logits: list[list[list[float]]],
    labels: list[list[int]],
) -> float:
    shift_logits, shift_labels = shift_for_next_token_loss(logits, labels)
    losses = [
        [
            negative_log_likelihood(
                softmax(shift_logits[sen_id][label_index]),
                label,
            )
            for label_index, label in enumerate(sen)
        ]
        for sen_id, sen in enumerate(shift_labels)
    ]
    total = 0
    loss_len = 0
    for loss_sen in losses:
        total += sum(loss_sen)
        loss_len += len(loss_sen)
    return total / loss_len
```

本轮踩坑：

- `enumerate(list)` 返回的是 `(index, value)`，不能直接把这个 tuple 当成数字下标或和 `int` 比较。
- `shift_logits` 对齐的是“当前位置预测下一个 token”，所以要去掉最后一个位置：`logits[:, :-1, :]`。
- `shift_labels` 是被预测的下一个 token，所以要去掉第一个 label：`labels[:, 1:]`。
- `negative_log_likelihood` 的输入应当是 probability distribution，不是原始 logits。
- 计算 `shifted_cross_entropy_loss` 时，每个位置的 logits 要先经过 `softmax`，再取正确 label 对应的概率做 `-log(probability)`。

可以进一步简化的写法：

```python
shift_logits = [batch_logits[:-1] for batch_logits in logits]
shift_labels = [batch_labels[1:] for batch_labels in labels]
```

验证命令：

```bash
PYTHONPATH=practice/src python3 -m unittest practice.tests.test_next_token_loss
```

## 反向传播与梯度更新

### 2026-05-21：导数、链式法则与梯度

训练闭环里，forward 负责算出预测和 loss，backward 负责沿着同一条计算路径反向计算梯度。

```text
forward:
input_ids -> embedding -> transformer -> hidden_states -> LM head -> logits -> loss

backward:
loss -> logits -> LM head -> transformer -> embedding
```

反向传播的起点可以理解为：

```text
d_loss / d_loss = 1
```

也就是从最终标量 loss 开始，逐层计算：

```text
d_loss / d_logits
d_loss / d_hidden_states
d_loss / d_W_lm
d_loss / d_attention_weights
d_loss / d_embedding_matrix
...
```

导数的核心含义是变化率。训练里更具体地说，是：

```text
参数发生微小变化时，loss 会朝哪个方向、以多大幅度变化。
```

所以：

```text
d_loss / d_w
```

不是普通的 `loss / w` 相除，而是：

```text
loss 的微小变化 / w 的微小变化
```

如果 `d_loss/d_w > 0`，说明 `w` 增大会让 loss 增大，optimizer 应该让 `w` 变小。
如果 `d_loss/d_w < 0`，说明 `w` 增大会让 loss 减小，optimizer 应该让 `w` 变大。

最简单的参数更新形式：

```text
w = w - learning_rate * gradient
```

### 导数公式与运行时梯度

一个关键区分：

```text
函数结构决定“怎么算梯度”。
当前 forward 的具体数值决定“这次梯度是多少”。
```

比如：

```text
y = w * x
loss = (y - target)^2
```

先根据函数结构推导通用公式：

```text
d_loss/d_w = 2 * (w * x - target) * x
```

然后在某一次训练 step 中代入当前值：

```text
w = 3
x = 2
target = 10

d_loss/d_w = 2 * (3 * 2 - 10) * 2 = -16
```

下一轮参数变成 `w = 4.6` 后，同一个公式会得到新的梯度：

```text
d_loss/d_w = 2 * (4.6 * 2 - 10) * 2 = -3.2
```

所以梯度像当前位置的一张局部快照：它描述的是当前参数点附近，loss 面的下降方向和斜率。

### 每层为什么要算输入梯度

每一层反向传播时通常会算两类梯度：

```text
1. d_loss/d_param：当前层参数的梯度，用于更新当前层参数
2. d_loss/d_input：当前层输入的梯度，用于继续传给上一层
```

以最小层为例：

```text
y = w * x
```

如果后面传回来：

```text
d_loss/d_y
```

那么当前层会根据链式法则计算：

```text
d_loss/d_w = d_loss/d_y * d_y/d_w = d_loss/d_y * x
d_loss/d_x = d_loss/d_y * d_y/d_x = d_loss/d_y * w
```

其中 `d_loss/d_w` 用来更新当前层参数 `w`，`d_loss/d_x` 不更新当前输入本身，而是传给上一层。

在神经网络里，当前层输入通常是上一层输出：

```text
h1 = Layer1(input)
h2 = Layer2(h1)
loss = Loss(h2)
```

Layer2 反向时会算：

```text
d_loss/d_W2  # 更新 Layer2 参数
d_loss/d_h1  # 传回 Layer1
```

Layer1 收到 `d_loss/d_h1` 后，再算：

```text
d_loss/d_W1  # 更新 Layer1 参数
d_loss/d_input
```

所以不会重复更新同一个东西：

```text
参数梯度用于更新本层参数。
输入梯度只是把 loss 的责任信号传回上一层。
```

### 矩阵乘法里的对应关系

神经网络里更常见的是矩阵乘法：

```text
Y = X @ W
```

如果后面传回来的输出梯度记为：

```text
G = d_loss/d_Y
```

那么：

```text
d_loss/d_W = X^T @ G
d_loss/d_X = G @ W^T
```

映射到 LM head：

```text
logits = hidden_states @ W_lm
```

反向时：

```text
d_loss/d_W_lm = hidden_states^T @ d_loss/d_logits
d_loss/d_hidden_states = d_loss/d_logits @ W_lm^T
```

`d_loss/d_W_lm` 用来更新 LM head 权重。
`d_loss/d_hidden_states` 继续传回最后一个 Transformer block。

### 是否会调整过头

每层同时计算参数梯度和输入梯度不会天然导致重复叠加，因为二者用途不同。

真正可能导致参数调整过头的是：

- learning rate 太大；
- 梯度本身过大；
- optimizer 设置不合适；
- 数据分布或训练过程不稳定。

因此训练系统通常会配合：

- learning rate schedule；
- gradient clipping；
- AdamW；
- warmup；
- normalization。

本轮心智模型：

```text
loss 是最终错误值。
gradient 是每个参数对 loss 的影响方向和影响强度。
backprop 是沿 forward 的反方向应用链式法则，把 loss 的责任信号传回每一层。
optimizer 才是真正修改参数的部分。
```

### 2026-05-22：Gradient / Backprop coding 练习

本轮搭好的练习入口：

- 源码入口：`practice/src/ai_practice/gradient_backprop.py`
- 测试入口：`practice/tests/test_gradient_backprop.py`
- 当前状态：测试已写好，源码函数暂时抛出 `NotImplementedError`，用于 TDD 红灯练习。

练习目标：

```text
1. 单参数梯度：
   y = w * x
   loss = (y - target)^2
   d_loss/d_w = 2 * (w*x - target) * x

2. 同时计算参数梯度和输入梯度：
   d_loss/d_y = 2 * (y - target)
   d_loss/d_w = d_loss/d_y * x
   d_loss/d_x = d_loss/d_y * w

3. 两层链式法则：
   h = w1 * x
   y = w2 * h
   loss = (y - target)^2

4. LM head 极简反向传播：
   logits = H @ W
   dW[i][j] = H[i] * d_logits[j]
   dH[i] = sum_j d_logits[j] * W[i][j]
```

待实现函数：

```python
def single_parameter_gradient(w, x, target):
    ...


def parameter_and_input_gradients(w, x, target):
    ...


def two_layer_chain_rule(x, w1, w2, target):
    ...


def lm_head_backward(hidden_state, weight, grad_logits):
    ...
```

验证命令：

```bash
PYTHONPATH=practice/src python3 -m unittest practice.tests.test_gradient_backprop
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

当前已经串起前向 loss 和反向梯度的核心关系：forward 得到 loss，backward 用链式法则计算每层参数梯度和输入梯度，optimizer 再基于参数梯度更新模型权重。

## 下一步

学习 optimizer，重点理解 SGD / AdamW 如何基于梯度、学习率和历史梯度状态更新参数。
