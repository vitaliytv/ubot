"""Unit-тести черг Redis (мок Redis)."""

from unittest.mock import patch

import pytest

from ubot_queue import (
    ADAPT_TASKS_KEY,
    OUTBOX_KEY,
    TASKS_KEY,
    pop_adapt_task,
    pop_outbox,
    pop_task,
    push_adapt_task,
    push_outbox_file,
    push_outbox_text,
    push_pdf_task,
)


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


def test_pop_task_returns_none_when_empty() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_get.return_value.brpop.return_value = None
        assert pop_task(timeout=1) is None


def test_pop_task_returns_parsed_payload() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_get.return_value.brpop.return_value = (
            TASKS_KEY,
            '{"chat_id": 10, "message_id": 2, "pdf_base64": "YQ==", "filename": "x.pdf"}',
        )
        result = pop_task(timeout=1)
    assert result is not None
    assert result["chat_id"] == 10 and result["message_id"] == 2
    assert result["pdf_base64"] == "YQ==" and result["filename"] == "x.pdf"


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


def test_pop_adapt_task_returns_none_when_empty() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_get.return_value.brpop.return_value = None
        assert pop_adapt_task(timeout=1) is None


def test_pop_adapt_task_returns_parsed_payload() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_get.return_value.brpop.return_value = (
            ADAPT_TASKS_KEY,
            '{"chat_id": 100, "message_id": 2, "text": "Hi", "filename_base": "doc"}',
        )
        result = pop_adapt_task(timeout=1)
    assert result is not None
    assert result["chat_id"] == 100 and result["message_id"] == 2
    assert result["text"] == "Hi" and result["filename_base"] == "doc"


def test_push_outbox_text_calls_lpush() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_client = mock_get.return_value
        push_outbox_text(chat_id=1, message_id=2, text="Hi")
        mock_client.lpush.assert_called_once()
        payload = mock_client.lpush.call_args[0][1]
        assert "1" in payload and "2" in payload and "text" in payload and "Hi" in payload


def test_push_outbox_file_calls_lpush() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_client = mock_get.return_value
        push_outbox_file(chat_id=1, message_id=2, content="data", filename="a.txt")
        mock_client.lpush.assert_called_once()
        payload = mock_client.lpush.call_args[0][1]
        assert "file" in payload and "a.txt" in payload


def test_pop_outbox_returns_none_when_empty() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_get.return_value.brpop.return_value = None
        assert pop_outbox(timeout=1) is None


def test_pop_outbox_returns_parsed_payload() -> None:
    with patch("ubot_queue.queue.get_redis_client") as mock_get:
        mock_get.return_value.brpop.return_value = (
            OUTBOX_KEY,
            '{"chat_id": 1, "message_id": 2, "type": "text", "body": "Hi"}',
        )
        result = pop_outbox(timeout=1)
    assert result is not None
    assert result["chat_id"] == 1 and result["message_id"] == 2
    assert result["type"] == "text" and result["body"] == "Hi"
