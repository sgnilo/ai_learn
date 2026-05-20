import math
import unittest

from ai_practice.transformer_block import TransformerBlock


class RecordingNorm:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls
        self.inputs = []

    def __call__(self, x: list[list[float]]) -> list[list[float]]:
        self.calls.append(self.name)
        self.inputs.append(x)
        return x


class RecordingSublayer:
    def __init__(self, name: str, calls: list[str], delta: list[list[float]]) -> None:
        self.name = name
        self.calls = calls
        self.delta = delta
        self.inputs = []

    def __call__(self, x: list[list[float]]) -> list[list[float]]:
        self.calls.append(self.name)
        self.inputs.append(x)
        return self.delta


class TransformerBlockTest(unittest.TestCase):
    def test_forward_applies_pre_norm_attention_and_ffn_with_residuals(self) -> None:
        calls = []
        norm1 = RecordingNorm("norm1", calls)
        attention = RecordingSublayer("attention", calls, [[0.1, 0.2]])
        norm2 = RecordingNorm("norm2", calls)
        ffn = RecordingSublayer("ffn", calls, [[0.3, 0.4]])

        block = TransformerBlock(norm1, attention, norm2, ffn)
        output = block.forward([[1.0, 2.0]])

        self.assertTrue(math.isclose(output[0][0], 1.4))
        self.assertTrue(math.isclose(output[0][1], 2.6))

        self.assertEqual(calls, ["norm1", "attention", "norm2", "ffn"])

    def test_second_norm_receives_attention_residual_output(self) -> None:
        calls = []
        norm1 = RecordingNorm("norm1", calls)
        attention = RecordingSublayer("attention", calls, [[0.1, 0.2]])
        norm2 = RecordingNorm("norm2", calls)
        ffn = RecordingSublayer("ffn", calls, [[0.3, 0.4]])

        block = TransformerBlock(norm1, attention, norm2, ffn)
        block.forward([[1.0, 2.0]])

        self.assertEqual(norm2.inputs[0], [[1.1, 2.2]])


if __name__ == "__main__":
    unittest.main()
