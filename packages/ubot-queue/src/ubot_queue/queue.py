"""Черги Redis: ubot:tasks, ubot:adapt_tasks, ubot:outbox."""

import base64
import json
import logging
import os

import redis

logger = logging.getLogger(__name__)

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
TASKS_KEY = "ubot:tasks"
ADAPT_TASKS_KEY = "ubot:adapt_tasks"
OUTBOX_KEY = "ubot:outbox"


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", DEFAULT_REDIS_URL)


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(get_redis_url(), decode_responses=True)


# --- PDF tasks (ubot:tasks) ---


def push_pdf_task(
    chat_id: int,
    message_id: int,
    pdf_base64: str,
    filename: str,
) -> None:
    """Додає задачу «обробити PDF» у чергу (з вмістом PDF у base64)."""
    client = get_redis_client()
    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id,
        "pdf_base64": pdf_base64,
        "filename": filename,
    })
    client.lpush(TASKS_KEY, payload)
    logger.info("Задачу додано в чергу: chat_id=%s message_id=%s", chat_id, message_id)


def pop_task(timeout: int = 5) -> dict | None:
    """Блокує і повертає одну задачу з ubot:tasks (BRPOP). Задача: chat_id, message_id, pdf_base64, filename."""
    client = get_redis_client()
    result = client.brpop(TASKS_KEY, timeout=timeout)
    if not result:
        return None
    _key, payload = result
    return json.loads(payload)


# --- Adapt tasks (ubot:adapt_tasks) ---


def push_adapt_task(
    *,
    chat_id: int,
    message_id: int,
    text: str,
    filename_base: str,
) -> None:
    """Додає задачу адаптації тексту в чергу (для ubot-adapt)."""
    client = get_redis_client()
    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "filename_base": filename_base,
    })
    client.lpush(ADAPT_TASKS_KEY, payload)


def pop_adapt_task(timeout: int = 5) -> dict | None:
    """Блокує і повертає одну задачу адаптації (BRPOP)."""
    client = get_redis_client()
    result = client.brpop(ADAPT_TASKS_KEY, timeout=timeout)
    if not result:
        return None
    _key, payload = result
    return json.loads(payload)


# --- Outbox (ubot:outbox). Контракт: {"chat_id", "message_id", "type": "text"|"file", "body"[, "filename"]} ---


def push_outbox_text(chat_id: int, message_id: int, text: str) -> None:
    """Додає текстове повідомлення в outbox (бот надішле його користувачу)."""
    client = get_redis_client()
    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id,
        "type": "text",
        "body": text,
    })
    client.lpush(OUTBOX_KEY, payload)


def push_outbox_file(
    chat_id: int,
    message_id: int,
    content: str,
    filename: str,
) -> None:
    """Додає файл у outbox (body — base64)."""
    client = get_redis_client()
    body_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id,
        "type": "file",
        "body": body_b64,
        "filename": filename,
    })
    client.lpush(OUTBOX_KEY, payload)


def pop_outbox(timeout: int = 1) -> dict | None:
    """Блокує і повертає одне повідомлення з outbox (BRPOP). Бот надсилає його користувачу."""
    client = get_redis_client()
    result = client.brpop(OUTBOX_KEY, timeout=timeout)
    if not result:
        return None
    _key, payload = result
    return json.loads(payload)
