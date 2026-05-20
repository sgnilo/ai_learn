class TransformerBlock:
    def __init__(self, norm1, attention, norm2, ffn) -> None:
        self.norm1 = norm1
        self.attention = attention
        self.norm2 = norm2
        self.ffn = ffn

    def forward(self, x: list[list[float]]) -> list[list[float]]:
        attention_delta = self.attention(self.norm1(x))
        x = add_vectors(x, attention_delta)

        ffn_delta = self.ffn(self.norm2(x))
        return add_vectors(x, ffn_delta)


def add_vectors(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [left_value + right[row_index][dim_index] for dim_index, left_value in enumerate(row)]
        for row_index, row in enumerate(left)
    ]
