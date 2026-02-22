"""Unit-тести адаптації тексту (мок моделі)."""

from unittest.mock import MagicMock, patch

import pytest

from ubot_adapt.adapt import adapt_text


def test_adapt_text_empty_returns_empty() -> None:
    assert adapt_text("") == ""
    assert adapt_text("   ") == ""


def test_adapt_text_returns_adapted_with_mock() -> None:
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
        tokenizer.decode.return_value = "Adapted text."
        mock_get.return_value = (tokenizer, model)
        result = adapt_text("Hello world")
    assert result == "Adapted text."
