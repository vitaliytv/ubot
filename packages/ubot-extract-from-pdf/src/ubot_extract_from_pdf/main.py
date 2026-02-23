"""Точка входу: запуск воркера експорту з PDF (без Telethon, тільки Redis)."""

import logging
import sys

from ubot_extract_from_pdf.worker import run_worker


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    run_worker()


if __name__ == "__main__":
    main()
