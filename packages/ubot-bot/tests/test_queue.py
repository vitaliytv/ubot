"""Тести інтеграції бота з чергою (мок ubot_queue)."""

from unittest.mock import patch

import pytest

from ubot_queue import TASKS_KEY, push_pdf_task


def test_push_pdf_task_calls_lpush() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_client = mock_get.return_value
        push_pdf_task(
            chat_id=123,
            message_id=456,
            pdf_base64="YQ==",
            filename="doc.pdf",
        )
        mock_client.lpush.assert_called_once()
        call_args = mock_client.lpush.call_args
        assert call_args[0][0] == TASKS_KEY
        payload = call_args[0][1]
        assert "123" in payload and "456" in payload and "YQ==" in payload and "doc.pdf" in payload