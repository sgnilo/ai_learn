from dataclasses import dataclass
import math


@dataclass
class RankedText:
    text: str
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("same dimensions")

    left_norm = math.sqrt(sum(x * x for x in left))
    right_norm = math.sqrt(sum(x * x for x in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    dot = sum(a * b for a, b in zip(left, right))
    return dot / (left_norm * right_norm)


class TextEmbeddingSimilarity:
    def __init__(self, embedding_model) -> None:
        self._embedding_model = embedding_model

    def score(self, left_text: str, right_text: str) -> float:
        vectors = self._embedding_model.embed_texts([left_text, right_text])
        return cosine_similarity(vectors[0], vectors[1])

    def rank(self, query: str, candidates: list[str]) -> list[RankedText]:
        scores = [RankedText(candidate, self.score(query, candidate)) for candidate in candidates]
        return sorted(scores, key=lambda x: x.score, reverse=True)
