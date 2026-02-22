"""Точка входу: запуск воркера експорту з PDF."""

import asyncio
import logging
import os
import sys

from ubot_extract_from_pdf.worker import run_worker


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

    missing = []
    if not api_id_str:
        missing.append("TELEGRAM_API_ID")
    if not api_hash:
        missing.append("TELEGRAM_API_HASH")
    if not bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")

    if missing:
        print(f"Потрібні змінні середовища: {', '.join(missing)}.", file=sys.stderr)
        sys.exit(1)

    try:
        api_id = int(api_id_str)
    except ValueError:
        print("TELEGRAM_API_ID має бути числом.", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_worker(api_id=api_id, api_hash=api_hash, bot_token=bot_token))


if __name__ == "__main__":
    main()
