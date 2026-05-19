import math
import unittest

from ai_practice.self_attention import (
    attention_scores,
    causal_self_attention,
    dot,
)


class SelfAttentionTest(unittest.TestCase):
    def test_dot_returns_vector_dot_product(self) -> None:
        self.assertEqual(dot([1.0, 2.0, 3.0], [4.0, 5.0, 6.0]), 32.0)

    def test_attention_scores_are_scaled_query_key_dot_products(self) -> None:
        scores = attention_scores(
            queries=[
                [1.0, 0.0],
                [0.0, 1.0],
            ],
            keys=[
                [1.0, 0.0],
                [1.0, 1.0],
            ],
        )

        scale = 1 / math.sqrt(2)
        self.assertTrue(math.isclose(scores[0][0], 1.0 * scale, rel_tol=1e-6))
        self.assertTrue(math.isclose(scores[0][1], 1.0 * scale, rel_tol=1e-6))
        self.assertEqual(scores[1][0], 0.0)
        self.assertTrue(math.isclose(scores[1][1], 1.0 * scale, rel_tol=1e-6))

    def test_causal_self_attention_prevents_future_values_from_affecting_output(self) -> None:
        outputs = causal_self_attention(
            queries=[
                [1.0, 0.0],
                [0.0, 1.0],
                [0.0, 3.0],
            ],
            keys=[
                [1.0, 0.0],
                [0.0, 1.0],
                [0.0, 3.0],
            ],
            values=[
                [10.0, 0.0],
                [0.0, 10.0],
                [999.0, 999.0],
            ],
        )

        self.assertEqual(outputs[0], [10.0, 0.0])
        self.assertTrue(math.isclose(outputs[1][0], 3.3023845, rel_tol=1e-6))
        self.assertTrue(math.isclose(outputs[1][1], 6.6976155, rel_tol=1e-6))
        self.assertGreater(outputs[2][0], 980.0)
        self.assertGreater(outputs[2][1], 980.0)


if __name__ == "__main__":
    unittest.main()
