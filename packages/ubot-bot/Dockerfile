# Збирати з кореня репо: docker build -f packages/ubot-bot/Dockerfile .
# Збірка лише з цього пакета (без кореня workspace).
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
WORKDIR /app
COPY packages/ubot-bot/ .
RUN uv lock && uv sync --no-dev

FROM python:3.14-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENTRYPOINT ["ubot-bot"]
