"""Telethon-бот: при отриманні PDF записує задачу в Redis."""

import logging
import os

from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import DocumentAttributeFilename, MessageMediaDocument

from ubot_bot.queue import push_pdf_task

logger = logging.getLogger(__name__)


def _is_pdf_document(media: MessageMediaDocument | None) -> bool:
    if not media or not media.document:
        return False
    for attr in media.document.attributes or []:
        if isinstance(attr, DocumentAttributeFilename) and (
            attr.file_name or ""
        ).lower().endswith(".pdf"):
            return True
    if getattr(media.document, "mime_type", None) == "application/pdf":
        return True
    return False


def _allowed_user_ids() -> set[int]:
    """Дозволені user_id з ALLOWED_USER_IDS (комою через кому)."""
    raw = (os.getenv("ALLOWED_USER_IDS") or "").strip()
    if not raw:
        return set()
    return {int(x.strip()) for x in raw.split(",") if x.strip()}


async def handle_message(
    event: NewMessage.Event, *, allowed_user_ids: set[int]
) -> None:
    """При PDF — пушимо задачу в Redis і відповідаємо. Тільки для дозволених user_id."""
    if allowed_user_ids and event.sender_id not in allowed_user_ids:
        await event.reply("Доступ до бота обмежено.")
        return
    message = event.message
    if not message.media or not _is_pdf_document(message.media):
        return
    chat_id = event.chat_id
    message_id = message.id
    logger.info("Отримано PDF (chat_id=%s message_id=%s)", chat_id, message_id)
    try:
        push_pdf_task(chat_id=chat_id, message_id=message_id)
        await event.reply("Задачу додано в чергу. Текстовий файл прийде незабаром.")
    except Exception as e:
        logger.exception("Помилка запису в Redis: %s", e)
        await event.reply(f"Помилка: {e!s}")


def create_client(
    api_id: int,
    api_hash: str,
    bot_token: str,
    session_name: str = "ubot_bot_session",
) -> TelegramClient:
    return TelegramClient(session_name, api_id, api_hash)


async def run_bot(
    api_id: int,
    api_hash: str,
    bot_token: str,
    *,
    allowed_user_ids: set[int] | None = None,
) -> None:
    if allowed_user_ids is None:
        allowed_user_ids = _allowed_user_ids()
    client = create_client(api_id, api_hash, bot_token)
    await client.start(bot_token=bot_token)
    client.add_event_handler(
        lambda e: handle_message(e, allowed_user_ids=allowed_user_ids),
        NewMessage(incoming=True, func=lambda e: bool(e.message.media)),
    )
    me = await client.get_me()
    logger.info("Бот запущено: @%s", me.username)
    await client.run_until_disconnected()
