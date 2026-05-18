"""A tiny character tokenizer for first-principles LLM practice."""

from __future__ import annotations


class CharTokenizer:
    """Encode text as character ids and decode ids back to text."""

    def __init__(self, corpus: str) -> None:
        if not corpus:
            raise ValueError("corpus must not be empty")

        UNKNOWN_TOKEN = "<unk>"
        self._chars = tuple(sorted(set(corpus)),) + (UNKNOWN_TOKEN,)
        self._char_to_id = {char: index for index, char in enumerate(self._chars)}
        self._id_to_char = {index: char for index, char in enumerate(self._chars)}
        self.UNKNOWN_TOKEN = UNKNOWN_TOKEN
        self.UNKNOWN_TOKEN_ID = self._char_to_id[UNKNOWN_TOKEN]

    @property
    def vocab_size(self) -> int:
        return len(self._chars)

    def encode(self, text: str) -> list[int]:
        try:
            result = []
            for char in text:
                result.append(self._char_to_id.get(char, self.UNKNOWN_TOKEN_ID))
            return result
        except KeyError as error:
            raise ValueError(f"unknown character: {error.args[0]!r}") from error

    def decode(self, token_ids: list[int]) -> str:
        try:
            raw = []
            for token_id in token_ids:
                if token_id not in self._id_to_char:
                    raw.append(self._id_to_char[self.UNKNOWN_TOKEN_ID])
                else:
                    raw.append(self._id_to_char[token_id])
            return "".join(raw)
        except KeyError as error:
            raise ValueError(f"unknown token id: {error.args[0]!r}") from error
