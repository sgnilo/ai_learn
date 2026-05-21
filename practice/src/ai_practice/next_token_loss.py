from ai_practice.softmax_logits import softmax
import math

def shift_for_next_token_loss(
    logits: list[list[list[float]]],
    labels: list[list[int]],
) -> tuple[list[list[list[float]]], list[list[int]]]:
    shift_logits = []
    for i, logit in enumerate(logits):
        new_logit = []
        for j, _ in enumerate(logit):
            if j < len(logits[i]) - 1:
                new_logit.append(logits[i][j])
        shift_logits.append(new_logit)
        new_logit = []

    shift_labels = []
    for i, label in enumerate(labels):
        new_label = []
        for j, _ in enumerate(label):
            if j > 0:
                new_label.append(labels[i][j])
        shift_labels.append(new_label)
        new_label = []

    return [shift_logits, shift_labels]


def negative_log_likelihood(
    probabilities: list[float],
    label: int,
) -> float:
    probability = probabilities[label]
    return -math.log(probability)


def shifted_cross_entropy_loss(
    logits: list[list[list[float]]],
    labels: list[list[int]],
) -> float:
    shift_logits, shift_labels = shift_for_next_token_loss(logits, labels)
    losses = [[ negative_log_likelihood(softmax(shift_logits[sen_id][label_index]), label) for label_index, label in enumerate(sen)] for sen_id, sen in enumerate(shift_labels)]
    total = 0
    loss_len = 0
    for loss_sen in losses:
        total += sum(loss_sen)
        loss_len += len(loss_sen)
    return total / loss_len