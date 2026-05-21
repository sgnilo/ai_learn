import math


def softmax(logits: list[float]) -> list[float]:
    exp_logits = [math.exp(logit) for logit in logits]
    exp_sum = sum(exp_logits)
    return [exp_logit / exp_sum for exp_logit in exp_logits]


def logits_to_probabilities(
    logits_by_position: list[list[float]],
) -> list[list[float]]:
    return [softmax(logits) for logits in logits_by_position]
