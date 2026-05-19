def build_causal_mask(seq_len: int) -> list[list[int]]:
    raise NotImplementedError


def apply_causal_mask(scores: list[list[float]]) -> list[list[float]]:
    raise NotImplementedError


def softmax(values: list[float]) -> list[float]:
    raise NotImplementedError


def weighted_sum(weights: list[float], values: list[list[float]]) -> list[float]:
    raise NotImplementedError


def masked_attention(
    scores: list[list[float]],
    values: list[list[float]],
) -> list[list[float]]:
    raise NotImplementedError
