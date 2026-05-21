import unittest

from ai_practice.lm_head import lm_head_logits


class LMHeadTest(unittest.TestCase):
    def test_lm_head_projects_hidden_states_to_vocab_logits(self) -> None:
        hidden_states = [
            [1.0, 2.0],
            [0.5, -1.0],
        ]
        lm_head = [
            [1.0, 0.0, -1.0],
            [0.0, 2.0, 1.0],
        ]

        self.assertEqual(
            lm_head_logits(hidden_states, lm_head),
            [
                [1.0, 4.0, 1.0],
                [0.5, -2.0, -1.5],
            ],
        )

    def test_lm_head_output_has_seq_len_by_vocab_size_shape(self) -> None:
        hidden_states = [
            [1.0, 2.0],
            [0.5, -1.0],
            [0.0, 3.0],
        ]
        lm_head = [
            [1.0, 0.0, -1.0, 2.0],
            [0.0, 2.0, 1.0, -1.0],
        ]

        logits = lm_head_logits(hidden_states, lm_head)

        self.assertEqual(len(logits), 3)
        self.assertEqual(len(logits[0]), 4)


if __name__ == "__main__":
    unittest.main()
