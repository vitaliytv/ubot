"""Воркер: бере задачу адаптації з Redis, адаптує текст, пушить логи і .txt в outbox."""

import logging

from ubot_adapt.adapt import adapt_text
from ubot_queue import pop_adapt_task, push_outbox_file, push_outbox_text

logger = logging.getLogger(__name__)


def process_one_task() -> bool:
    """Бере одну задачу з ubot:adapt_tasks, адаптує текст, пушить логи і файл в outbox."""
    task = pop_adapt_task(timeout=5)
    if not task:
        return False
    chat_id = task["chat_id"]
    message_id = task["message_id"]
    text = task["text"]
    filename_base = task.get("filename_base", "document")
    logger.info("Адаптую текст для chat_id=%s (%d символів)", chat_id, len(text))
    try:
        push_outbox_text(chat_id, message_id, "📋 Воркер адаптації: отримано задачу.")
        push_outbox_text(chat_id, message_id, "📋 Адаптую текст (Llama)…")
        adapted = adapt_text(text)
        if not adapted.strip():
            adapted = text
            logger.warning("Модель повернула порожній результат, відправляю оригінал")
        out_name = f"{filename_base}_adapted.txt"
        push_outbox_text(chat_id, message_id, f"📋 Відправляю адаптований файл {out_name}…")
        push_outbox_file(chat_id, message_id, adapted, out_name)
        logger.info("Відправлено %s в outbox (%d символів)", out_name, len(adapted))
        push_outbox_text(chat_id, message_id, "Готово.")
    except Exception as e:
        logger.exception("Помилка адаптації: %s", e)
        push_outbox_text(chat_id, message_id, f"Помилка адаптації тексту: {e!s}")
    return True


def run_worker() -> None:
    """Головний цикл: обробка задач з Redis (без Telethon)."""
    logger.info("Воркер адаптації запущено, очікую задачі в Redis…")
    while True:
        try:
            process_one_task()
        except Exception as e:
            logger.exception("Помилка циклу: %s", e)
