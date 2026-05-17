import unittest

from ai_practice import CharTokenizer


class CharTokenizerTest(unittest.TestCase):
    def test_round_trip(self) -> None:
        tokenizer = CharTokenizer("hello world")

        token_ids = tokenizer.encode("hello")

        self.assertEqual(tokenizer.decode(token_ids), "hello")
        self.assertEqual(tokenizer.vocab_size, len(set("hello world")))

    def test_rejects_unknown_character(self) -> None:
        tokenizer = CharTokenizer("abc")

        with self.assertRaisesRegex(ValueError, "unknown character"):
            tokenizer.encode("abcd")

    def test_rejects_unknown_token_id(self) -> None:
        tokenizer = CharTokenizer("abc")

        with self.assertRaisesRegex(ValueError, "unknown token id"):
            tokenizer.decode([0, 99])


if __name__ == "__main__":
    unittest.main()
