"""Vietnamese Kokoro artifacts and text segmentation.

The checkpoint, vocabulary and voicepacks must come from the same release:
https://huggingface.co/contextboxai/Kokoro-Vietnamese
"""

import re
import unicodedata

VI_MODEL_REPO = "contextboxai/Kokoro-Vietnamese"
VI_MODEL_REVISION = "9f210d622209fcc216fe2ac6159fed2ff381cb8a"
VI_VOICES = {
    "diem_trinh": "Diễm Trinh",
    "duc_an": "Đức An",
    "duc_duy": "Đức Duy",
    "hung_thinh": "Hưng Thịnh",
    "mai_linh": "Mai Linh",
    "mai_loan": "Mai Loan",
    "manh_dung": "Mạnh Dũng",
    "my_yen": "Mỹ Yến",
    "ngoc_huyen": "Ngọc Huyền",
    "phat_tai": "Phát Tài",
    "storyvert": "storyvert",
    "thanh_dat": "Thành Đạt",
    "thuc_trinh": "Thục Trinh",
    "tuan_ngoc": "Tuấn Ngọc",
}


def iter_phoneme_segments(text, phonemize, max_phonemes):
    """Split at sentences, then words, without discarding long paragraphs."""
    if max_phonemes < 1:
        raise ValueError("Vietnamese model has no usable phoneme context")
    text = unicodedata.normalize("NFC", text)

    def fit(segment):
        phonemes = phonemize(segment)
        if not phonemes:
            return
        if len(phonemes) <= max_phonemes:
            yield segment, phonemes
            return
        words = segment.split()
        if len(words) < 2:
            raise ValueError("A Vietnamese word exceeds the model context; shorten it")
        middle = len(words) // 2
        yield from fit(" ".join(words[:middle]))
        yield from fit(" ".join(words[middle:]))

    for sentence in re.split(r"(?<=[.!?…])\s+|\n+", text):
        sentence = re.sub(r"\s+", " ", sentence).strip()
        if sentence:
            yield from fit(sentence)


def compatible_state_dict(weights, expected):
    """Adapt modern/removed weight normalization to Kokoro 0.9.4 parameters.

    Fine-tuning checkpoints use DataParallel prefixes and either the new
    parametrization API or plain convolution weights. The legacy loader's
    strict=False fallback silently leaves those layers randomly initialized.
    """
    import torch

    converted = {}
    for name, value in weights.items():
        name = name.removeprefix("module.")
        name = name.replace("parametrizations.weight.original0", "weight_g")
        name = name.replace("parametrizations.weight.original1", "weight_v")
        if name.endswith("weight") and name not in expected:
            stem = name[:-len("weight")]
            gain_name, vector_name = stem + "weight_g", stem + "weight_v"
            if gain_name in expected and vector_name in expected:
                if value.shape != expected[vector_name].shape:
                    raise ValueError(f"Checkpoint shape mismatch for {name}")
                gain_shape = expected[gain_name].shape
                reduce_dims = tuple(index for index, size in enumerate(gain_shape) if size == 1)
                gain = torch.linalg.vector_norm(value, dim=reduce_dims, keepdim=True)
                if gain.shape != gain_shape:
                    raise ValueError(f"Weight normalization shape mismatch for {name}")
                # Zero filters must stay zero without dividing zero by zero.
                converted[gain_name] = gain
                converted[vector_name] = torch.where(gain == 0, torch.ones_like(value), value)
                continue
        if name in converted:
            raise ValueError(f"Duplicate checkpoint parameter: {name}")
        converted[name] = value
    return converted


def load_vietnamese_weights(model, checkpoint):
    """Reload every VI component strictly after compatibility conversion."""
    import torch

    checkpoint_weights = torch.load(checkpoint, weights_only=True, map_location="cpu")
    for component, weights in checkpoint_weights.items():
        layer = getattr(model, component)
        converted = compatible_state_dict(weights, layer.state_dict())
        # Kokoro's inference AdaIN wrapper enables affine InstanceNorm for
        # ONNX export. VI training does not store these extra scale/offset
        # parameters; their identity values reproduce non-affine training.
        for name, normalization in layer.named_modules():
            if isinstance(normalization, torch.nn.InstanceNorm1d) and normalization.affine:
                prefix = name + "." if name else ""
                gain, bias = prefix + "weight", prefix + "bias"
                if gain not in converted and bias not in converted:
                    converted[gain] = torch.ones_like(normalization.weight)
                    converted[bias] = torch.zeros_like(normalization.bias)
        layer.load_state_dict(converted, strict=True)
