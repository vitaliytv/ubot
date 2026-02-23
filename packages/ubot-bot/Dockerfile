# Збирати з кореня репо: docker build -f packages/ubot-bot/Dockerfile .
# Копіюємо лише ubot-queue + цей пакет; pyproject фільтруємо під цей workspace.
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages/ubot-queue ./packages/ubot-queue
COPY packages/ubot-bot ./packages/ubot-bot
COPY scripts/filter-workspace-pyproject.py ./
RUN python3 filter-workspace-pyproject.py ubot-bot && uv lock && uv sync --package ubot-bot --no-dev

FROM python:3.14-alpine
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["ubot-bot"]
