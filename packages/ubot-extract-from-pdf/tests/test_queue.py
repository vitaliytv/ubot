"""Unit-тести черги (мок Redis через ubot_queue)."""

from unittest.mock import patch

import pytest

from ubot_queue import ADAPT_TASKS_KEY, push_adapt_task


def test_push_adapt_task_calls_lpush() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_client = mock_get.return_value
        push_adapt_task(
            chat_id=100,
            message_id=2,
            text="Hello",
            filename_base="doc",
        )
        mock_client.lpush.assert_called_once()
        call_args = mock_client.lpush.call_args
        assert call_args[0][0] == ADAPT_TASKS_KEY
        payload = call_args[0][1]
        assert "100" in payload and "2" in payload and "Hello" in payload and "doc" in payload
