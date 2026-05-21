import math
import unittest

from ai_practice.next_token_loss import (
    negative_log_likelihood,
    shift_for_next_token_loss,
    shifted_cross_entropy_loss,
)
from ai_practice.softmax_logits import softmax


class NextTokenLossTest(unittest.TestCase):
    def test_shift_for_next_token_loss_aligns_logits_with_next_labels(self) -> None:
        logits = [
            [
                [1.0, 4.0, 1.0],
                [3.0, 1.0, 0.0],
                [0.0, 0.0, 5.0],
            ]
        ]
        labels = [[0, 1, 2]]

        shift_logits, shift_labels = shift_for_next_token_loss(logits, labels)

        self.assertEqual(
            shift_logits,
            [
                [
                    [1.0, 4.0, 1.0],
                    [3.0, 1.0, 0.0],
                ]
            ],
        )
        self.assertEqual(shift_labels, [[1, 2]])

    def test_negative_log_likelihood_uses_correct_label_probability(self) -> None:
        loss = negative_log_likelihood([0.1, 0.7, 0.2], label=1)

        self.assertTrue(math.isclose(loss, -math.log(0.7), rel_tol=1e-6))

    def test_shifted_cross_entropy_loss_averages_all_shifted_positions(self) -> None:
        logits = [
            [
                [1.0, 4.0, 1.0],
                [3.0, 1.0, 0.0],
                [0.0, 0.0, 5.0],
            ]
        ]
        labels = [[0, 1, 2]]

        first_loss = -math.log(softmax([1.0, 4.0, 1.0])[1])
        second_loss = -math.log(softmax([3.0, 1.0, 0.0])[2])
        expected_loss = (first_loss + second_loss) / 2

        loss = shifted_cross_entropy_loss(logits, labels)

        self.assertTrue(math.isclose(loss, expected_loss, rel_tol=1e-6))


if __name__ == "__main__":
    unittest.main()
