def lm_head_logits(
    hidden_states: list[list[float]],
    lm_head: list[list[float]],
) -> list[list[float]]:
    vocab_size = len(lm_head[0])
    logits = [[0.0 for _ in range(vocab_size)] for _ in hidden_states]

    for token_index, hidden_vector in enumerate(hidden_states):
        for vocab_index in range(vocab_size):
            for hidden_index, hidden_value in enumerate(hidden_vector):
                logits[token_index][vocab_index] += hidden_value * lm_head[hidden_index][vocab_index]

    return logits
