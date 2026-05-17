import unittest

from ai_practice import CharTokenizer


class CharTokenizerTest(unittest.TestCase):
    def test_round_trip(self) -> None:
        tokenizer = CharTokenizer("hello world")

        token_ids = tokenizer.encode("hei")

        self.assertEqual(tokenizer.decode(token_ids), "he<unk>")
        self.assertEqual(tokenizer.vocab_size, len(set("hello world")) + 1)

    def test_rejects_unknown_character(self) -> None:
        tokenizer = CharTokenizer("abc")
        token_ids = tokenizer.encode("hei")

        self.assertEqual(tokenizer.decode(token_ids), "<unk><unk><unk>")

    def test_rejects_unknown_token_id(self) -> None:
        tokenizer = CharTokenizer("abc")

        self.assertEqual(tokenizer.decode([0, 99]), "a<unk>")


if __name__ == "__main__":
    unittest.main()
