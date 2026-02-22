#!/usr/bin/env sh
# Ін'єкція змінних через утиліту env з файла .env (у корені проєкту).
# Використання: ./scripts/run-with-env.sh ubot-bot   або   ./scripts/run-with-env.sh ubot-extract-from-pdf

set -e
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  echo "Файл .env не знайдено." >&2
  exit 1
fi
# Експорт рядків KEY=VALUE з .env (без коментарів і порожніх рядків), потім запуск команди через env
export $(grep -v '^#' .env | grep -v '^$' | xargs)
exec env uv run "$@"
