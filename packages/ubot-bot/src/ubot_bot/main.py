"""Точка входу: запуск бота (запис задач у Redis)."""

import asyncio
import logging
import os
import sys

from ubot_bot.bot import run_bot


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    api_id_str = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    allowed_ids_str = os.getenv("ALLOWED_USER_IDS", "").strip()
    missing = []
    if not api_id_str:
        missing.append("TELEGRAM_API_ID")
    if not api_hash:
        missing.append("TELEGRAM_API_HASH")
    if not bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not allowed_ids_str:
        missing.append("ALLOWED_USER_IDS")

    if missing:
        print(
            f"Потрібні змінні середовища: {', '.join(missing)}.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        api_id = int(api_id_str)
    except ValueError:
        print("TELEGRAM_API_ID має бути числом.", file=sys.stderr)
        sys.exit(1)

    try:
        allowed_user_ids = {
            int(x.strip()) for x in allowed_ids_str.split(",") if x.strip()
        }
    except ValueError:
        print(
            "ALLOWED_USER_IDS має бути списком числових id через кому (наприклад: 292188676,8418087262).",
            file=sys.stderr,
        )
        sys.exit(1)

    asyncio.run(
        run_bot(
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            allowed_user_ids=allowed_user_ids,
        )
    )


if __name__ == "__main__":
    main()
