import math


def build_causal_mask(seq_len: int) -> list[list[int]]:
    mask = []
    for i in range(seq_len):
        line = []
        for j in range(seq_len):
            if i >= j:
                line.append(1)
            else:
                line.append(0)
        mask.append(line)
    return mask


def apply_causal_mask(scores: list[list[float]]) -> list[list[float]]:
    masked_scores = []
    for i, row in enumerate(scores):
        masked_row = []
        for j, score in enumerate(row):
            if i < j:
                masked_row.append(-float("inf"))
            else:
                masked_row.append(score)
        masked_scores.append(masked_row)
    return masked_scores


def softmax(values: list[float]) -> list[float]:
    exp_values = [math.exp(val) for val in values]
    total = sum(exp_values)
    return [val / total for val in exp_values]


def weighted_sum(weights: list[float], values: list[list[float]]) -> list[float]:
    output = [0.0 for _ in range(len(values[0]))]
    for i in range(len(values)):
        for j in range(len(values[0])):
            output[j] += values[i][j] * weights[i]
    return output


def masked_attention(
    scores: list[list[float]],
    values: list[list[float]],
) -> list[list[float]]:
    masked_scores = apply_causal_mask(scores)
    weights_for_all_token = [softmax(line) for line in masked_scores]
    output = []
    for weights in weights_for_all_token:
        output.append(weighted_sum(weights, values))
    return output
