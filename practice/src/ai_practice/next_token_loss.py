from ai_practice.softmax_logits import softmax

def shift_for_next_token_loss(
    logits: list[list[list[float]]],
    labels: list[list[int]],
) -> tuple[list[list[list[float]]], list[list[int]]]:
    raise NotImplementedError


def negative_log_likelihood(
    probabilities: list[float],
    label: int,
) -> float:
    raise NotImplementedError


def shifted_cross_entropy_loss(
    logits: list[list[list[float]]],
    labels: list[list[int]],
) -> float:
    raise NotImplementedError
