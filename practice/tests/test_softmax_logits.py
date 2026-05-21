import math
import unittest

from ai_practice.softmax_logits import logits_to_probabilities, softmax


class SoftmaxLogitsTest(unittest.TestCase):
    def test_softmax_converts_logits_to_probabilities(self) -> None:
        probabilities = softmax([1.0, 4.0, 1.0])

        self.assertTrue(math.isclose(probabilities[0], 0.0452785, rel_tol=1e-6))
        self.assertTrue(math.isclose(probabilities[1], 0.9094430, rel_tol=1e-6))
        self.assertTrue(math.isclose(probabilities[2], 0.0452785, rel_tol=1e-6))
        self.assertTrue(math.isclose(sum(probabilities), 1.0, rel_tol=1e-6))

    def test_logits_to_probabilities_applies_softmax_per_position(self) -> None:
        probabilities = logits_to_probabilities(
            [
                [1.0, 4.0, 1.0],
                [0.5, -2.0, -1.5],
            ]
        )

        self.assertEqual(len(probabilities), 2)
        self.assertEqual(len(probabilities[0]), 3)
        self.assertTrue(math.isclose(sum(probabilities[0]), 1.0, rel_tol=1e-6))
        self.assertTrue(math.isclose(sum(probabilities[1]), 1.0, rel_tol=1e-6))
        self.assertGreater(probabilities[0][1], probabilities[0][0])
        self.assertGreater(probabilities[1][0], probabilities[1][1])


if __name__ == "__main__":
    unittest.main()
