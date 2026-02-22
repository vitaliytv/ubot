# Збирати з кореня репо: docker build -f packages/ubot-extract-from-pdf/Dockerfile .
# Збірка лише з цього пакета (без кореня workspace).
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
WORKDIR /app
COPY packages/ubot-extract-from-pdf/ .
RUN uv lock && uv sync --no-dev

FROM python:3.14-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENTRYPOINT ["ubot-extract-from-pdf"]
