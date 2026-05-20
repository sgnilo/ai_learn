import math

from ai_practice.causal_mask import masked_attention

def dot(left: list[float], right: list[float]) -> float:
    return sum(left_value * right_value for left_value, right_value in zip(left, right))


def attention_scores(
    queries: list[list[float]],
    keys: list[list[float]],
) -> list[list[float]]:
    d_k = len(queries[0])
    return [[dot(query, key) / math.sqrt(d_k) for key in keys] for query in queries]


def causal_self_attention(
    queries: list[list[float]],
    keys: list[list[float]],
    values: list[list[float]],
) -> list[list[float]]:
    scores = attention_scores(queries, keys)
    return masked_attention(scores, values)
