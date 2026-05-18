class SimpleEmbedding:
    def __init__(self, embedding_matrix: list[list[float]]) -> None:
        self._embedding_matrix = embedding_matrix

    def lookup_one(self, token_id: int) -> list[float]:
        if token_id < 0:
            raise ValueError(f"invalid token id: {token_id}")

        try:
            return self._embedding_matrix[token_id]
        except IndexError:
            raise ValueError(f"invalid token id: {token_id}") from None

    def lookup_sequence(self, token_ids: list[int]) -> list[list[float]]:
        return [self.lookup_one(token_id) for token_id in token_ids]

    def lookup_batch(self, batch_token_ids: list[list[int]]) -> list[list[list[float]]]:
        return [self.lookup_sequence(token_ids) for token_ids in batch_token_ids]
