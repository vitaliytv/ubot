"""Воркер: бере задачу з Redis (PDF у base64), експортує текст, пушить .txt і логи в outbox, задачу в чергу адаптації."""

import base64
import logging
from pathlib import Path

from ubot_extract_from_pdf.pdf import extract_text_from_pdf_bytes
from ubot_queue import (
    pop_task,
    push_adapt_task,
    push_outbox_file,
    push_outbox_text,
)

logger = logging.getLogger(__name__)


def process_one_task() -> bool:
    """Бере одну задачу з Redis, витягує текст з PDF, пушить логи і .txt в outbox, задачу адаптації в чергу."""
    task = pop_task(timeout=5)
    if not task:
        return False
    chat_id = task["chat_id"]
    message_id = task["message_id"]
    pdf_base64 = task.get("pdf_base64")
    filename = task.get("filename") or "document.pdf"
    if not pdf_base64:
        logger.warning("Задача без pdf_base64")
        push_outbox_text(chat_id, message_id, "Помилка: задача без вмісту PDF.")
        return True
    logger.info("Обробляю задачу: chat_id=%s message_id=%s", chat_id, message_id)
    try:
        push_outbox_text(chat_id, message_id, "📋 Воркер: завантажую PDF…")
        raw = base64.b64decode(pdf_base64)
        push_outbox_text(chat_id, message_id, "📋 Витягую текст з PDF…")
        text = extract_text_from_pdf_bytes(raw)
        if not text.strip():
            push_outbox_text(chat_id, message_id, "У PDF не знайдено тексту.")
            return True
        base_name = Path(filename).stem
        out_name = f"{base_name}.txt"
        push_outbox_text(chat_id, message_id, f"📋 Відправляю текстовий файл {out_name}…")
        push_outbox_file(chat_id, message_id, text, out_name)
        logger.info("Відправлено %s в outbox (%d символів)", out_name, len(text))
        push_outbox_text(
            chat_id,
            message_id,
            "Готово. Задачу додано в чергу адаптації — незабаром прийде адаптований текст.",
        )
        push_adapt_task(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            filename_base=base_name,
        )
        logger.info("Задачу адаптації додано в чергу")
    except Exception as e:
        logger.exception("Помилка обробки задачі: %s", e)
        push_outbox_text(chat_id, message_id, f"Помилка обробки PDF: {e!s}")
    return True


def run_worker() -> None:
    """Головний цикл: обробка задач з Redis (без Telethon)."""
    logger.info("Воркер extract-from-pdf запущено, очікую задачі в Redis…")
    while True:
        try:
            process_one_task()
        except Exception as e:
            logger.exception("Помилка циклу воркера: %s", e)
