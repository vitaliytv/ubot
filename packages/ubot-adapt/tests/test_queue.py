"""Unit-тести черги адаптації (мок Redis)."""

from unittest.mock import patch

import pytest

from ubot_adapt.queue import ADAPT_TASKS_KEY, pop_adapt_task


def test_pop_adapt_task_returns_none_when_empty() -> None:
    with patch("ubot_adapt.queue.get_redis_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.brpop.return_value = None
        result = pop_adapt_task(timeout=1)
    assert result is None


def test_pop_adapt_task_returns_parsed_payload() -> None:
    with patch("ubot_adapt.queue.get_redis_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.brpop.return_value = (
            ADAPT_TASKS_KEY,
            '{"chat_id": 100, "message_id": 2, "text": "Hi", "filename_base": "doc"}',
        )
        result = pop_adapt_task(timeout=1)
    assert result is not None
    assert result["chat_id"] == 100
    assert result["message_id"] == 2
    assert result["text"] == "Hi"
    assert result["filename_base"] == "doc"
