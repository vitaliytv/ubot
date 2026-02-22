"""Воркер: бере задачу з Redis, експортує текст з PDF, відправляє .txt і пушить у чергу адаптації."""

import logging
from io import BytesIO
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeFilename, MessageMediaDocument

from ubot_extract_from_pdf.pdf import extract_text_from_pdf_bytes
from ubot_extract_from_pdf.queue import pop_task, push_adapt_task

logger = logging.getLogger(__name__)


def _pdf_filename(media: MessageMediaDocument | None) -> str:
    if not media or not media.document:
        return "document.pdf"
    for attr in media.document.attributes or []:
        if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
            return attr.file_name
    return "document.pdf"


async def _log_to_chat(client: TelegramClient, chat_id: int, message_id: int, text: str) -> None:
    """Відправляє рядок логу в чат (користувач бачить хід роботи воркера)."""
    try:
        await client.send_message(chat_id, f"📋 {text}", reply_to=message_id)
    except Exception:
        pass


async def process_one_task(client: TelegramClient) -> bool:
    """Бере одну задачу з Redis, експортує текст, відправляє .txt користувачу і пушить у чергу адаптації."""
    task = pop_task(timeout=5)
    if not task:
        return False
    chat_id = task["chat_id"]
    message_id = task["message_id"]
    logger.info("Обробляю задачу: chat_id=%s message_id=%s", chat_id, message_id)
    try:
        await _log_to_chat(client, chat_id, message_id, "Воркер: завантажую PDF…")
        message = await client.get_messages(chat_id, ids=message_id)
        if not message or not message.media:
            logger.warning("Повідомлення не знайдено або без медіа")
            await _log_to_chat(client, chat_id, message_id, "Помилка: повідомлення або файл не знайдено.")
            return True
        data = await client.download_media(message, bytes)
        if not data:
            await client.send_message(chat_id, "Не вдалося завантажити файл.", reply_to=message_id)
            return True
        await _log_to_chat(client, chat_id, message_id, "Витягую текст з PDF…")
        text = extract_text_from_pdf_bytes(data)
        if not text.strip():
            await client.send_message(chat_id, "У PDF не знайдено тексту.", reply_to=message_id)
            return True
        base = Path(_pdf_filename(message.media)).stem
        out_name = f"{base}.txt"
        await _log_to_chat(client, chat_id, message_id, f"Відправляю текстовий файл {out_name}…")
        # 1) Відправляємо .txt користувачу
        file_obj = BytesIO(text.encode("utf-8"))
        file_obj.name = out_name
        await client.send_file(chat_id, file_obj, reply_to=message_id)
        logger.info("Відправлено %s користувачу (%d символів)", out_name, len(text))
        await _log_to_chat(client, chat_id, message_id, "Готово. Задачу додано в чергу адаптації — незабаром прийде адаптований текст.")
        # 2) Пушимо задачу в чергу адаптації
        push_adapt_task(chat_id=chat_id, message_id=message_id, text=text, filename_base=base)
        logger.info("Задачу адаптації додано в чергу")
    except Exception as e:
        logger.exception("Помилка обробки задачі: %s", e)
        try:
            await client.send_message(
                chat_id,
                f"Помилка обробки PDF: {e!s}",
                reply_to=message_id,
            )
        except Exception:
            pass
    return True


async def run_worker(
    api_id: int,
    api_hash: str,
    bot_token: str,
) -> None:
    client = TelegramClient("ubot_extract_from_pdf_session", api_id, api_hash)
    await client.start(bot_token=bot_token)
    me = await client.get_me()
    logger.info("Воркер extract-from-pdf запущено (@%s), очікую задачі в Redis…", me.username)
    while True:
        try:
            await process_one_task(client)
        except Exception as e:
            logger.exception("Помилка циклу воркера: %s", e)
