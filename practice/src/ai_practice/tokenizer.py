"""A tiny character tokenizer for first-principles LLM practice."""

from __future__ import annotations


class CharTokenizer:
    """Encode text as character ids and decode ids back to text."""

    def __init__(self, corpus: str) -> None:
        if not corpus:
            raise ValueError("corpus must not be empty")

        self._chars = tuple(sorted(set(corpus)))
        self._char_to_id = {char: index for index, char in enumerate(self._chars)}
        self._id_to_char = {index: char for index, char in enumerate(self._chars)}

    @property
    def vocab_size(self) -> int:
        return len(self._chars)

    def encode(self, text: str) -> list[int]:
        try:
            return [self._char_to_id[char] for char in text]
        except KeyError as error:
            raise ValueError(f"unknown character: {error.args[0]!r}") from error

    def decode(self, token_ids: list[int]) -> str:
        try:
            return "".join(self._id_to_char[token_id] for token_id in token_ids)
        except KeyError as error:
            raise ValueError(f"unknown token id: {error.args[0]!r}") from error
