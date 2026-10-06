"""Regression coverage for bounded Vietnamese phoneme segmentation."""

import unittest
import unicodedata

from kokoro_tts_local.vietnamese import compatible_state_dict, iter_phoneme_segments, load_vietnamese_weights


class VietnameseSegmentationTests(unittest.TestCase):
    def test_long_text_preserves_every_word_within_context(self):
        words = [f"từ{index}" for index in range(120)]
        text = " ".join(words)
        segments = list(iter_phoneme_segments(text, lambda value: value, 45))
        self.assertGreater(len(segments), 1)
        self.assertEqual(" ".join(part for part, _ in segments).split(), words)
        self.assertTrue(all(len(phonemes) <= 45 for _, phonemes in segments))

    def test_sentence_and_newline_boundaries_preserve_vietnamese_accents(self):
        text = unicodedata.normalize("NFD", "Xin chào.\nTôi đọc tiếng Việt! Tạm biệt.")
        segments = list(iter_phoneme_segments(text, lambda value: value, 510))
        self.assertEqual([part for part, _ in segments], [
            "Xin chào.", "Tôi đọc tiếng Việt!", "Tạm biệt.",
        ])

    def test_unsplittable_input_fails_without_silent_truncation(self):
        with self.assertRaises(ValueError):
            list(iter_phoneme_segments("x" * 600, lambda value: value, 510))
        self.assertEqual(list(iter_phoneme_segments(" \n ", lambda value: value, 510)), [])


class VietnameseCheckpointTests(unittest.TestCase):
    def test_modern_normalization_preserves_convolution_output(self):
        import torch
        from torch import nn

        source = torch.nn.utils.parametrizations.weight_norm(nn.Conv1d(2, 3, 3))
        target = torch.nn.utils.weight_norm(nn.Conv1d(2, 3, 3))
        weights = {"module." + name: value for name, value in source.state_dict().items()}
        target.load_state_dict(compatible_state_dict(weights, target.state_dict()), strict=True)
        signal = torch.arange(24, dtype=torch.float32).reshape(1, 2, 12) / 24
        torch.testing.assert_close(target(signal), source(signal))

    def test_plain_weights_and_zero_filters_preserve_convolution_output(self):
        import torch
        from torch import nn

        source = nn.Conv1d(2, 3, 3)
        with torch.no_grad():
            source.weight[0].zero_()
        target = torch.nn.utils.weight_norm(nn.Conv1d(2, 3, 3))
        weights = {"module." + name: value for name, value in source.state_dict().items()}
        target.load_state_dict(compatible_state_dict(weights, target.state_dict()), strict=True)
        signal = torch.arange(24, dtype=torch.float32).reshape(1, 2, 12) / 24
        torch.testing.assert_close(target(signal), source(signal))

    def test_incomplete_weights_cannot_be_silently_accepted(self):
        import torch
        from torch import nn

        target = torch.nn.utils.weight_norm(nn.Conv1d(2, 3, 3))
        with self.assertRaises(RuntimeError):
            target.load_state_dict(compatible_state_dict({}, target.state_dict()), strict=True)

    def test_checkpoint_loader_preserves_non_affine_training_and_rejects_missing_convolution(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace
        import torch
        from torch import nn

        source = nn.Sequential(
            nn.InstanceNorm1d(3, affine=False),
            torch.nn.utils.parametrizations.weight_norm(nn.Conv1d(3, 2, 3)),
        )
        target = nn.Sequential(
            nn.InstanceNorm1d(3, affine=True),
            torch.nn.utils.weight_norm(nn.Conv1d(3, 2, 3)),
        )
        weights = {"module." + name: value for name, value in source.state_dict().items()}
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "vietnamese.pth"
            torch.save({"decoder": weights}, checkpoint)
            load_vietnamese_weights(SimpleNamespace(decoder=target), checkpoint)
            signal = torch.arange(36, dtype=torch.float32).reshape(1, 3, 12) / 36
            torch.testing.assert_close(target(signal), source(signal))
            del weights["module.1.bias"]
            torch.save({"decoder": weights}, checkpoint)
            with self.assertRaises(RuntimeError):
                load_vietnamese_weights(SimpleNamespace(decoder=target), checkpoint)


if __name__ == "__main__":
    unittest.main()
