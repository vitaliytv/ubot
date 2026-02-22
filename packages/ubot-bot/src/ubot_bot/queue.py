"""Черга задач у Redis (list)."""

import json
import logging
import os

import redis

logger = logging.getLogger(__name__)

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
TASKS_KEY = "ubot:tasks"


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", DEFAULT_REDIS_URL)


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(get_redis_url(), decode_responses=True)


def push_pdf_task(chat_id: int, message_id: int) -> None:
    """Додає задачу «обробити PDF» у чергу Redis."""
    client = get_redis_client()
    payload = json.dumps({"chat_id": chat_id, "message_id": message_id})
    client.lpush(TASKS_KEY, payload)
    logger.info("Задачу додано в чергу: chat_id=%s message_id=%s", chat_id, message_id)
