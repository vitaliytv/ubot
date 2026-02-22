"""Черга задач у Redis — спільний контракт з ubot-bot."""

import json
import os

import redis

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
TASKS_KEY = "ubot:tasks"
ADAPT_TASKS_KEY = "ubot:adapt_tasks"


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", DEFAULT_REDIS_URL)


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(get_redis_url(), decode_responses=True)


def pop_task(timeout: int = 5) -> dict | None:
    """Блокує і повертає одну задачу з черги (BRPOP). Повертає None при таймауті."""
    client = get_redis_client()
    result = client.brpop(TASKS_KEY, timeout=timeout)
    if not result:
        return None
    _key, payload = result
    return json.loads(payload)


def push_adapt_task(*, chat_id: int, message_id: int, text: str, filename_base: str) -> None:
    """Додає задачу адаптації тексту в чергу (для ubot-adapt)."""
    client = get_redis_client()
    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "filename_base": filename_base,
    })
    client.lpush(ADAPT_TASKS_KEY, payload)
