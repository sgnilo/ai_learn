import unittest

from ai_practice.embedding import SimpleEmbedding


class SimpleEmbeddingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.embedding = SimpleEmbedding(
            [
                [0.1, 0.2],
                [0.3, 0.4],
                [0.5, 0.6],
            ]
        )

    def test_lookup_one_returns_token_vector(self) -> None:
        self.assertEqual(self.embedding.lookup_one(1), [0.3, 0.4])

    def test_lookup_sequence_returns_seq_len_by_hidden_size(self) -> None:
        self.assertEqual(
            self.embedding.lookup_sequence([0, 2]),
            [
                [0.1, 0.2],
                [0.5, 0.6],
            ],
        )

    def test_lookup_batch_returns_batch_by_seq_len_by_hidden_size(self) -> None:
        self.assertEqual(
            self.embedding.lookup_batch([[0, 2], [1, 0]]),
            [
                [
                    [0.1, 0.2],
                    [0.5, 0.6],
                ],
                [
                    [0.3, 0.4],
                    [0.1, 0.2],
                ],
            ],
        )

    def test_rejects_unknown_token_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid token id: 99"):
            self.embedding.lookup_one(99)

    def test_rejects_negative_token_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid token id: -1"):
            self.embedding.lookup_one(-1)


if __name__ == "__main__":
    unittest.main()
