# ubot

Телеграм-бот асистент: експорт тексту з PDF. UV monorepo: бот (Telethon) записує задачі в Redis, воркер виконує їх (PyMuPDF).

## Архітектура

- **ubot-bot** (пакет `packages/ubot-bot`): Telethon-бот — при отриманні PDF пушить задачу в Redis list `ubot:tasks`.
- **ubot-extract-from-pdf** (пакет `packages/ubot-extract-from-pdf`): бере задачі з Redis, завантажує PDF, витягує текст (PyMuPDF), **відправляє .txt користувачу** і пушить задачу адаптації в `ubot:adapt_tasks`.
- **ubot-adapt** (пакет `packages/ubot-adapt`): бере задачі з `ubot:adapt_tasks`, адаптує текст за допомогою **Llama-3.1-8B-Instruct** (прибрати технічні фрагменти, логічні блоки, спрощення, заголовки тощо), відправляє користувачу .txt.

Потрібен запущений **Redis** і одна й та сама черга для бота та воркера. Змінні середовища інжектяться через утиліту **env** (у Docker — через `env_file` і `command: exec env ...`; локально — **poe** зчитує `.env` і запускає команди).

## Локальний запуск (Docker Compose)

З кореня проєкту, з заповненим `.env` (TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_BOT_TOKEN):

```bash
docker compose up --build
```

Піднімуться Redis, ubot-bot, ubot-extract-from-pdf і ubot-adapt. Логи всіх сервісів — в одному потоці. Для фону: `docker compose up -d --build`.

## Локальний запуск (uv, без Docker)

1. Встановити [uv](https://docs.astral.sh/uv/) і Redis (наприклад `brew install redis` та `redis-server`).

2. З кореня проєкту:

   ```bash
   uv sync
   ```

3. Файл `.env` у корені:

   ```env
   TELEGRAM_API_ID=...
   TELEGRAM_API_HASH=...
   TELEGRAM_BOT_TOKEN=...
   REDIS_URL=redis://localhost:6379/0
   # Для ubot-adapt (модель Llama-3.1-8B-Instruct на Hugging Face, gated)
   HF_TOKEN=your_huggingface_token
   ```

4. Запуск через **poe** (скрипт запуску; poe зчитує `.env` і інжектить змінні):

   **Бот** (один термінал):
   ```bash
   poe bot
   ```

   **Воркер експорту з PDF** (другий термінал):
   ```bash
   poe extract-from-pdf
   ```

   **Воркер адаптації тексту (Llama)** (третій термінал, опційно GPU):
   ```bash
   poe adapt
   ```

Користувач надсилає PDF боту → бот відповідає «Задачу додано в чергу» → ubot-extract-from-pdf витягує текст, **відправляє .txt користувачу** і пушить у чергу адаптації → ubot-adapt адаптує текст (Llama 3.1 8B) і надсилає адаптований .txt у чат.

## Структура (monorepo)

```
packages/
  ubot-bot/     # Telethon, запис у Redis
  ubot-extract-from-pdf/  # Redis + PyMuPDF: експорт → .txt користувачу + черга адаптації
  ubot-adapt/   # Redis + Llama-3.1-8B-Instruct, адаптація тексту → .txt користувачу
```

## Тести

У кожному пакеті свої тести (за потреби). З кореня після `uv sync`:

```bash
uv run --package ubot-bot pytest packages/ubot-bot -v
uv run --package ubot-extract-from-pdf pytest packages/ubot-extract-from-pdf -v
```

## Деплой

- GKE: окремі деплойменти для бота та воркера, спільний Redis (наприклад Memorystore).
- CI/CD: GitHub Actions (збірка образів для обох пакетів).

## Ліцензія

Див. [LICENSE](LICENSE).
