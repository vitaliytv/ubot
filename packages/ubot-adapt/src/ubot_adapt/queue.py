"""Черга задач адаптації (ubot:adapt_tasks)."""

import json
import os

import redis

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
ADAPT_TASKS_KEY = "ubot:adapt_tasks"


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", DEFAULT_REDIS_URL)


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(get_redis_url(), decode_responses=True)


def pop_adapt_task(timeout: int = 5) -> dict | None:
    """Блокує і повертає одну задачу адаптації (BRPOP)."""
    client = get_redis_client()
    result = client.brpop(ADAPT_TASKS_KEY, timeout=timeout)
    if not result:
        return None
    _key, payload = result
    return json.loads(payload)
