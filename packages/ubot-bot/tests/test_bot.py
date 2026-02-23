"""Unit-тести для бота (перевірка PDF, дозволені користувачі)."""

from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from telethon.events import NewMessage
from telethon.tl.types import Document, DocumentAttributeFilename, MessageMediaDocument

from ubot_bot.bot import _is_pdf_document, handle_message


def test_is_pdf_document_none() -> None:
    assert _is_pdf_document(None) is False


def test_is_pdf_document_no_document() -> None:
    media = MagicMock(spec=MessageMediaDocument)
    media.document = None
    assert _is_pdf_document(media) is False


def test_is_pdf_document_by_filename() -> None:
    doc = MagicMock(spec=Document)
    doc.attributes = [DocumentAttributeFilename(file_name="file.pdf")]
    media = MagicMock(spec=MessageMediaDocument)
    media.document = doc
    assert _is_pdf_document(media) is True


def test_is_pdf_document_by_mime_type() -> None:
    doc = MagicMock(spec=Document)
    doc.attributes = []
    doc.mime_type = "application/pdf"
    media = MagicMock(spec=MessageMediaDocument)
    media.document = doc
    assert _is_pdf_document(media) is True


def test_is_pdf_document_non_pdf() -> None:
    doc = MagicMock(spec=Document)
    doc.attributes = [DocumentAttributeFilename(file_name="file.txt")]
    doc.mime_type = "text/plain"
    media = MagicMock(spec=MessageMediaDocument)
    media.document = doc
    assert _is_pdf_document(media) is False


@pytest.mark.asyncio
async def test_handle_message_rejects_disallowed_user() -> None:
    event = MagicMock(spec=NewMessage.Event)
    event.sender_id = 999
    event.message = MagicMock()
    event.reply = AsyncMock()
    allowed = {292188676, 8418087262}
    await handle_message(event, allowed_user_ids=allowed)
    event.reply.assert_called_once_with("Доступ до бота обмежено.")


@pytest.mark.asyncio
async def test_handle_message_pdf_pushes_task_and_replies() -> None:
    event = MagicMock(spec=NewMessage.Event)
    event.sender_id = 292188676
    event.chat_id = 100
    event.message = MagicMock()
    event.message.id = 1
    event.message.media = MagicMock()
    event.reply = AsyncMock()
    event.client = MagicMock()
    event.client.download_media = AsyncMock(return_value=b"pdf bytes")
    with patch("ubot_bot.bot._is_pdf_document", return_value=True), patch(
        "ubot_bot.bot._get_pdf_filename", return_value="file.pdf"
    ), patch("ubot_bot.bot.push_pdf_task") as mock_push:
        await handle_message(event, allowed_user_ids={292188676})
        mock_push.assert_called_once()
        call = mock_push.call_args
        assert call.kwargs["chat_id"] == 100
        assert call.kwargs["message_id"] == 1
        assert call.kwargs["filename"] == "file.pdf"
        assert isinstance(call.kwargs["pdf_base64"], str)
        assert len(call.kwargs["pdf_base64"]) > 0
        assert event.reply.call_count == 2
        event.reply.assert_any_call("📋 Завантажую файл…")
        event.reply.assert_any_call(
            "Задачу додано в чергу. Текстовий файл прийде незабаром."
        )
