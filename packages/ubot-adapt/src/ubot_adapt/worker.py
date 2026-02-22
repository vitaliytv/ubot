"""Воркер: бере задачу адаптації з Redis, адаптує текст через Llama, відправляє .txt."""

import logging
from io import BytesIO

from telethon import TelegramClient

from ubot_adapt.adapt import adapt_text
from ubot_adapt.queue import pop_adapt_task

logger = logging.getLogger(__name__)


async def _log_to_chat(client: TelegramClient, chat_id: int, message_id: int, text: str) -> None:
    """Відправляє рядок логу в чат (користувач бачить хід роботи воркера)."""
    try:
        await client.send_message(chat_id, f"📋 {text}", reply_to=message_id)
    except Exception:
        pass


async def process_one_task(client: TelegramClient) -> bool:
    """Бере одну задачу з ubot:adapt_tasks, адаптує текст, відправляє файл."""
    task = pop_adapt_task(timeout=5)
    if not task:
        return False
    chat_id = task["chat_id"]
    message_id = task["message_id"]
    text = task["text"]
    filename_base = task.get("filename_base", "document")
    logger.info("Адаптую текст для chat_id=%s (%d символів)", chat_id, len(text))
    try:
        await _log_to_chat(client, chat_id, message_id, "Воркер адаптації: отримано задачу.")
        await _log_to_chat(client, chat_id, message_id, "Адаптую текст (Llama)…")
        adapted = adapt_text(text)
        if not adapted.strip():
            adapted = text
            logger.warning("Модель повернула порожній результат, відправляю оригінал")
        out_name = f"{filename_base}_adapted.txt"
        await _log_to_chat(client, chat_id, message_id, f"Відправляю адаптований файл {out_name}…")
        file_obj = BytesIO(adapted.encode("utf-8"))
        file_obj.name = out_name
        await client.send_file(chat_id, file_obj, reply_to=message_id)
        logger.info("Відправлено %s (%d символів)", out_name, len(adapted))
        await _log_to_chat(client, chat_id, message_id, "Готово.")
    except Exception as e:
        logger.exception("Помилка адаптації: %s", e)
        try:
            await client.send_message(
                chat_id,
                f"Помилка адаптації тексту: {e!s}",
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
    client = TelegramClient("ubot_adapt_session", api_id, api_hash)
    await client.start(bot_token=bot_token)
    me = await client.get_me()
    logger.info("Воркер адаптації запущено (@%s), очікую задачі…", me.username)
    while True:
        try:
            await process_one_task(client)
        except Exception as e:
            logger.exception("Помилка циклу: %s", e)
