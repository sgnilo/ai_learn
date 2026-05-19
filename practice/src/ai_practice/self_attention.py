def dot(left: list[float], right: list[float]) -> float:
    raise NotImplementedError


def attention_scores(
    queries: list[list[float]],
    keys: list[list[float]],
) -> list[list[float]]:
    raise NotImplementedError


def causal_self_attention(
    queries: list[list[float]],
    keys: list[list[float]],
    values: list[list[float]],
) -> list[list[float]]:
    raise NotImplementedError
