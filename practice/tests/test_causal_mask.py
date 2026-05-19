import math
import unittest

from ai_practice.causal_mask import (
    apply_causal_mask,
    build_causal_mask,
    masked_attention,
    softmax,
    weighted_sum,
)


class CausalMaskTest(unittest.TestCase):
    def test_build_causal_mask_returns_lower_triangle(self) -> None:
        self.assertEqual(
            build_causal_mask(5),
            [
                [1, 0, 0, 0, 0],
                [1, 1, 0, 0, 0],
                [1, 1, 1, 0, 0],
                [1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
            ],
        )

    def test_apply_causal_mask_replaces_future_scores_with_negative_infinity(self) -> None:
        scores = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]

        self.assertEqual(
            apply_causal_mask(scores),
            [
                [1.0, -float("inf"), -float("inf")],
                [1.0, 2.0, -float("inf")],
                [1.0, 2.0, 3.0],
            ],
        )

    def test_softmax_turns_negative_infinity_into_zero_probability(self) -> None:
        weights = softmax([1.0, 2.0, -float("inf")])

        self.assertTrue(math.isclose(weights[0], 0.26894142, rel_tol=1e-6))
        self.assertTrue(math.isclose(weights[1], 0.73105858, rel_tol=1e-6))
        self.assertEqual(weights[2], 0.0)
        self.assertTrue(math.isclose(sum(weights), 1.0, rel_tol=1e-6))

    def test_weighted_sum_combines_value_vectors_by_attention_weights(self) -> None:
        self.assertEqual(
            weighted_sum(
                [0.25, 0.75, 0.0],
                [
                    [10.0, 0.0],
                    [0.0, 10.0],
                    [999.0, 999.0],
                ],
            ),
            [2.5, 7.5],
        )

    def test_masked_attention_prevents_future_values_from_affecting_output(self) -> None:
        scores = [
            [1.0, 2.0, 9.0],
            [1.0, 2.0, 9.0],
            [1.0, 2.0, 9.0],
        ]
        values = [
            [10.0, 0.0],
            [0.0, 10.0],
            [999.0, 999.0],
        ]

        outputs = masked_attention(scores, values)

        self.assertEqual(outputs[0], [10.0, 0.0])
        self.assertTrue(math.isclose(outputs[1][0], 2.6894142, rel_tol=1e-6))
        self.assertTrue(math.isclose(outputs[1][1], 7.3105858, rel_tol=1e-6))
        self.assertGreater(outputs[2][0], 990.0)
        self.assertGreater(outputs[2][1], 990.0)


if __name__ == "__main__":
    unittest.main()
