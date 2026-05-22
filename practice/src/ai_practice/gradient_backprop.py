def single_parameter_gradient(
    w: float,
    x: float,
    target: float,
) -> tuple[float, float, float]:
    raise NotImplementedError


def parameter_and_input_gradients(
    w: float,
    x: float,
    target: float,
) -> tuple[float, float, float, float, float]:
    raise NotImplementedError


def two_layer_chain_rule(
    x: float,
    w1: float,
    w2: float,
    target: float,
) -> tuple[float, float, float, float, float, float, float, float]:
    raise NotImplementedError


def lm_head_backward(
    hidden_state: list[float],
    weight: list[list[float]],
    grad_logits: list[float],
) -> tuple[list[float], list[list[float]], list[float]]:
    raise NotImplementedError
