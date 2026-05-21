def softmax(logits: list[float]) -> list[float]:
    raise NotImplementedError


def logits_to_probabilities(
    logits_by_position: list[list[float]],
) -> list[list[float]]:
    raise NotImplementedError
