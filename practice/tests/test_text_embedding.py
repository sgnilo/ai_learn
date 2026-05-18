import json
import math
import unittest
from pathlib import Path

from ai_practice.text_embedding import TextEmbeddingSimilarity, cosine_similarity


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "text_embedding_cases.json"


class FakeEmbeddingModel:
    """Deterministic stand-in for a real embedding model used by tests."""

    _vectors = {
        "How do I request a refund?": [1.0, 0.0, 0.0],
        "What is the refund process?": [0.9, 0.1, 0.0],
        "How do I change my profile avatar?": [0.0, 1.0, 0.0],
        "I forgot my password and cannot sign in.": [0.0, 1.0, 0.0],
        "How can I reset my login password?": [0.1, 0.9, 0.0],
        "Where can I download my invoice?": [1.0, 0.0, 0.0],
        "function getUserProfileById returns user profile data": [0.0, 0.0, 1.0],
        "get user profile by id from the user service": [0.0, 0.1, 0.9],
        "company refund policy and cancellation rules": [1.0, 0.0, 0.0],
    }

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._vectors[text] for text in texts]


class TextEmbeddingSimilarityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.similarity = TextEmbeddingSimilarity(FakeEmbeddingModel())
        self.cases = json.loads(FIXTURE_PATH.read_text())["cases"]

    def test_cosine_similarity_returns_expected_value(self) -> None:
        score = cosine_similarity([1.0, 0.0], [1.0, 1.0])

        self.assertTrue(math.isclose(score, 0.70710678, rel_tol=1e-6))

    def test_cosine_similarity_rejects_mismatched_dimensions(self) -> None:
        with self.assertRaisesRegex(ValueError, "same dimensions"):
            cosine_similarity([1.0, 0.0], [1.0])

    def test_positive_text_scores_higher_than_negative_text(self) -> None:
        for case in self.cases:
            with self.subTest(case=case["id"]):
                positive_score = self.similarity.score(case["query"], case["positive"])
                negative_score = self.similarity.score(case["query"], case["negative"])

                self.assertGreater(positive_score, negative_score)

    def test_rank_returns_most_similar_text_first(self) -> None:
        case = self.cases[0]

        ranked = self.similarity.rank(
            case["query"],
            [
                case["negative"],
                case["positive"],
            ],
        )

        self.assertEqual(ranked[0].text, case["positive"])
        self.assertGreater(ranked[0].score, ranked[1].score)


if __name__ == "__main__":
    unittest.main()
