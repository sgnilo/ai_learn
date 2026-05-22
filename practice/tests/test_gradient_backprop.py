import unittest

from ai_practice.gradient_backprop import (
    lm_head_backward,
    parameter_and_input_gradients,
    single_parameter_gradient,
    two_layer_chain_rule,
)


class GradientBackpropTest(unittest.TestCase):
    def test_single_parameter_gradient(self) -> None:
        y, loss, grad_w = single_parameter_gradient(w=2.0, x=3.0, target=10.0)

        self.assertEqual(y, 6.0)
        self.assertEqual(loss, 16.0)
        self.assertEqual(grad_w, -24.0)

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
