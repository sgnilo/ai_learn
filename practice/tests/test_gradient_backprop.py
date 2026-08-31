import unittest

from ai_practice.gradient_backprop import (
    lm_head_backward,
    parameter_and_input_gradients,
    single_parameter_gradient,
    two_layer_chain_rule,
)


class GradientBackpropTest(unittest.TestCase):
    # 题目 1：单参数梯度。
    #
    # 参数：
    # - w=2: 当前层参数。
    # - x=3: 当前层输入。
    # - target=10: 目标值。
    #
    # 要验证：
    # - y = 2 * 3 = 6。
    # - loss = (6 - 10)^2 = 16。
    # - grad_w = 2 * (w*x - target) * x = 2 * (6 - 10) * 3 = -24。
    #
    # 附加信息：
    # - grad_w 为负，表示增大 w 会让 loss 下降。
    def test_single_parameter_gradient(self) -> None:
        y, loss, grad_w = single_parameter_gradient(w=2.0, x=3.0, target=10.0)

        self.assertEqual(y, 6.0)
        self.assertEqual(loss, 16.0)
        self.assertEqual(grad_w, -24.0)

    # 题目 2：参数梯度和输入梯度。
    #
    # 参数：
    # - w=4: 当前层参数。
    # - x=2: 当前层输入。
    # - target=6: 目标值。
    #
    # 要验证：
    # - y = 4 * 2 = 8。
    # - loss = (8 - 6)^2 = 4。
    # - grad_y = 2 * (8 - 6) = 4。
    # - grad_w = grad_y * x = 4 * 2 = 8。
    # - grad_x = grad_y * w = 4 * 4 = 16。
    #
    # 附加信息：
    # - grad_w 用来更新本层参数。
    # - grad_x 用来传给上一层，帮助上一层继续计算自己的参数梯度。
    def test_parameter_and_input_gradients(self) -> None:
        y, loss, grad_y, grad_w, grad_x = parameter_and_input_gradients(
            w=4.0,
            x=2.0,
            target=6.0,
        )

        self.assertEqual(y, 8.0)
        self.assertEqual(loss, 4.0)
        self.assertEqual(grad_y, 4.0)
        self.assertEqual(grad_w, 8.0)
        self.assertEqual(grad_x, 16.0)

    # 题目 3：两层链式法则。
    #
    # 参数：
    # - x=2: 第一层输入。
    # - w1=3: 第一层参数。
    # - w2=4: 第二层参数。
    # - target=20: 目标值。
    #
    # 前向：
    # - h = w1 * x = 3 * 2 = 6。
    # - y = w2 * h = 4 * 6 = 24。
    # - loss = (24 - 20)^2 = 16。
    #
    # 反向：
    # - grad_y = 2 * (y - target) = 8。
    # - grad_w2 = grad_y * h = 8 * 6 = 48。
    # - grad_h = grad_y * w2 = 8 * 4 = 32。
    # - grad_w1 = grad_h * x = 32 * 2 = 64。
    # - grad_x = grad_h * w1 = 32 * 3 = 96。
    #
    # 附加信息：
    # - grad_h 是第二层传给第一层的梯度。
    # - 第一层不是直接用 grad_y，而是用 grad_h 继续反推。
    def test_two_layer_chain_rule(self) -> None:
        h, y, loss, grad_y, grad_w2, grad_h, grad_w1, grad_x = (
            two_layer_chain_rule(x=2.0, w1=3.0, w2=4.0, target=20.0)
        )

        self.assertEqual(h, 6.0)
        self.assertEqual(y, 24.0)
        self.assertEqual(loss, 16.0)
        self.assertEqual(grad_y, 8.0)
        self.assertEqual(grad_w2, 48.0)
        self.assertEqual(grad_h, 32.0)
        self.assertEqual(grad_w1, 64.0)
        self.assertEqual(grad_x, 96.0)

    # 题目 4：极简 LM head backward。
    #
    # 参数：
    # - hidden_state=[2, 1]: Transformer 传给 LM head 的输入向量。
    # - weight: LM head 权重矩阵，2 个 hidden 维度映射到 3 个 vocab token。
    # - grad_logits=[0.2, -0.5, 0.3]: loss 层传回来的 d_loss/d_logits。
    #
    # 前向：
    # - logits = hidden_state @ weight = [2, 3, 5]。
    #
    # 反向：
    # - grad_weight[i][j] = hidden_state[i] * grad_logits[j]。
    # - grad_hidden_state[i] = sum_j grad_logits[j] * weight[i][j]。
    #
    # 附加信息：
    # - grad_weight 用于更新 LM head 参数。
    # - grad_hidden_state 继续传回 Transformer block。
    def test_lm_head_backward(self) -> None:
        hidden_state = [2.0, 1.0]
        weight = [
            [1.0, 0.0, 2.0],
            [0.0, 3.0, 1.0],
        ]
        grad_logits = [0.2, -0.5, 0.3]

        logits, grad_weight, grad_hidden_state = lm_head_backward(
            hidden_state,
            weight,
            grad_logits,
        )

        self.assertEqual(logits, [2.0, 3.0, 5.0])
        self.assertEqual(
            grad_weight,
            [
                [0.4, -1.0, 0.6],
                [0.2, -0.5, 0.3],
            ],
        )
        self.assertEqual(grad_hidden_state, [0.8, -1.2])


if __name__ == "__main__":
    unittest.main()
