"""Тест адаптації вмісту файла source.txt (фікстура)."""

import os
from pathlib import Path

import pytest

from ubot_adapt.adapt import adapt_text

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SOURCE_TXT = FIXTURES_DIR / "source.txt"


def _read_source() -> str:
    return SOURCE_TXT.read_text(encoding="utf-8")


def test_adapt_file_source_with_mock() -> None:
    """Читає source.txt, адаптує через мок моделі — результат не порожній і відрізняється від входу."""
    from unittest.mock import MagicMock, patch

    source = _read_source()
    assert source.strip(), "фікстура source.txt не повинна бути порожньою"

    with patch("ubot_adapt.adapt._get_adapter") as mock_get:
        tokenizer = MagicMock()
        tokenizer.apply_chat_template.return_value = "prompt"
        tokenizer.eos_token_id = 0
        enc = MagicMock()
        enc.to.return_value = enc
        enc.__getitem__ = lambda self, k: MagicMock(shape=(1, 10)) if k == "input_ids" else None
        tokenizer.return_value = enc
        model = MagicMock()
        model.device = "cpu"
        gen_out = MagicMock()
        gen_out.__getitem__.return_value = MagicMock()
        model.generate.return_value = gen_out
        tokenizer.decode.return_value = "Adapted text from source file."
        mock_get.return_value = (tokenizer, model)

        result = adapt_text(source)

    assert result == "Adapted text from source file."
    assert result != source


def _has_hf_token() -> bool:
    return bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"))


@pytest.mark.skipif(
    not _has_hf_token(),
    reason="Потрібен HF_TOKEN для реальної моделі",
)
def test_adapt_file_source_integration() -> None:
    """Інтеграційний тест: читає source.txt і адаптує реальною моделлю (повільно, потрібен HF_TOKEN)."""
    source = _read_source()
    assert source.strip()

    result = adapt_text(source)

    assert result.strip(), "модель повинна повернути непустий адаптований текст"
    assert result != source, "адаптований текст повинен відрізнятися від оригіналу"
