import math


# 练习 1：单参数梯度。
#
# 题意：
# - 只模拟一个最小线性层，前向公式是 y = w * x。
# - 再用平方误差计算 loss = (y - target)^2。
# - 你要手动算出参数 w 对最终 loss 的梯度 d_loss/d_w。
#
# 参数说明：
# - w: 当前层唯一的可训练参数，类似神经网络里的一个 weight。
# - x: 当前层输入。这里把它当作已知输入，不在本题中更新。
# - target: 训练目标，也就是希望 y 靠近的正确值。
#
# 返回值说明：
# - y: 当前 forward 的预测结果。
# - loss: 当前预测和 target 之间的平方误差。
# - grad_w: d_loss/d_w，用于后续 optimizer 更新 w。
#
# 附加信息：
# - 依赖链路是 w -> y -> loss。
# - 推导公式是 d_loss/d_w = 2 * (w*x - target) * x。
def single_parameter_gradient(
    w: float,
    x: float,
    target: float,
) -> tuple[float, float, float]:
    y = w * x
    loss = math.pow(y - target, 2)
    grad_w = 2 * x * (w * x - target)
    return [y, loss, grad_w]



# 练习 2：同时计算参数梯度和输入梯度。
#
# 题意：
# - 前向公式仍然是 y = w * x，loss = (y - target)^2。
# - 这次不只算参数 w 的梯度，还要算输入 x 的梯度。
# - 这对应反向传播里“当前层既要更新自己的参数，也要把梯度传回上一层”。
#
# 参数说明：
# - w: 当前层参数，需要计算 d_loss/d_w。
# - x: 当前层输入，需要计算 d_loss/d_x 并继续传给上一层。
# - target: 训练目标。
#
# 返回值说明：
# - y: 当前 forward 的预测结果。
# - loss: 当前平方误差。
# - grad_y: d_loss/d_y，loss 对当前层输出 y 的梯度。
# - grad_w: d_loss/d_w，用于更新当前层参数 w。
# - grad_x: d_loss/d_x，用于传给上一层，不是用来直接更新 x。
#
# 附加信息：
# - grad_y = 2 * (y - target)。
# - grad_w = grad_y * x。
# - grad_x = grad_y * w。
def parameter_and_input_gradients(
    w: float,
    x: float,
    target: float,
) -> tuple[float, float, float, float, float]:
    y = w * x
    loss = math.pow(y - target, 2)
    grad_y = 2 * (w * x - target)
    grad_w = 2 * x * (w * x - target)
    grad_x = 2 * w * (w * x - target)
    return [y, loss, grad_y, grad_w, grad_x]




# 练习 3：两层链式法则。
#
# 题意：
# - 模拟两个连续的线性层：
#   1. 第一层：h = w1 * x
#   2. 第二层：y = w2 * h
#   3. 损失：loss = (y - target)^2
# - 你要从 loss 往回推，先算第二层的梯度，再把 d_loss/d_h 传回第一层。
#
# 参数说明：
# - x: 第一层输入。
# - w1: 第一层参数，需要计算 d_loss/d_w1。
# - w2: 第二层参数，需要计算 d_loss/d_w2。
# - target: 训练目标。
#
# 返回值说明：
# - h: 第一层输出，也是第二层输入。
# - y: 第二层输出，也是最终预测。
# - loss: 当前平方误差。
# - grad_y: d_loss/d_y，loss 对最终输出 y 的梯度。
# - grad_w2: d_loss/d_w2，第二层参数梯度。
# - grad_h: d_loss/d_h，第二层传回第一层的输入梯度。
# - grad_w1: d_loss/d_w1，第一层参数梯度。
# - grad_x: d_loss/d_x，继续传给更前面一层的输入梯度。
#
# 附加信息：
# - 反向链路是 loss -> y -> h -> x。
# - grad_w2 = grad_y * h。
# - grad_h = grad_y * w2。
# - grad_w1 = grad_h * x。
# - grad_x = grad_h * w1。
def two_layer_chain_rule(
    x: float,
    w1: float,
    w2: float,
    target: float,
) -> tuple[float, float, float, float, float, float, float, float]:
    h = x * w1
    y, loss, grad_y, grad_w2, grad_h= parameter_and_input_gradients(w2, h, target)
    grad_w1 = x * grad_h
    grad_x = w1 * grad_h
    return [h, y, loss, grad_y, grad_w2, grad_h, grad_w1, grad_x]


# 练习 4：极简 LM head backward。
#
# 题意：
# - 模拟 LM head 的最后一层投影。
# - 前向公式是 logits = hidden_state @ weight。
# - loss 层已经完成 softmax/cross entropy 的反向计算，并传回 grad_logits。
# - 你要根据 grad_logits 计算 LM head 的参数梯度和输入梯度。
#
# 参数说明：
# - hidden_state: Transformer 最后一层给 LM head 的输入向量，shape 是 [hidden_size]。
# - weight: LM head 权重矩阵，shape 是 [hidden_size, vocab_size]。
# - grad_logits: d_loss/d_logits，shape 是 [vocab_size]。
#
# 返回值说明：
# - logits: 前向计算得到的 vocab 分数，shape 是 [vocab_size]。
# - grad_weight: d_loss/d_weight，shape 和 weight 一样，用于更新 LM head 权重。
# - grad_hidden_state: d_loss/d_hidden_state，shape 是 [hidden_size]，传回 Transformer。
#
# 附加信息：
# - logits[j] = sum_i hidden_state[i] * weight[i][j]。
# - grad_weight[i][j] = hidden_state[i] * grad_logits[j]。
# - grad_hidden_state[i] = sum_j grad_logits[j] * weight[i][j]。
def lm_head_backward(
    hidden_state: list[float],
    weight: list[list[float]],
    grad_logits: list[float],
) -> tuple[list[float], list[list[float]], list[float]]:
    logits = []
    for k, w_col in enumerate(weight[0]):
        sum_a = 0
        for i, row in enumerate(hidden_state):
            sum_a += weight[i][k] * hidden_state[i]
        logits.append(sum_a)
        sum_a = 0
    # logit = sum(logits) / len(logits)
    grad_logits 
    d_logits / d_weight[i][j] = 

    

