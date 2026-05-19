class TransformerBlock:
    def __init__(self, norm1, attention, norm2, ffn) -> None:
        self.norm1 = norm1
        self.attention = attention
        self.norm2 = norm2
        self.ffn = ffn

    def forward(self, x: list[list[float]]) -> list[list[float]]:
        raise NotImplementedError
