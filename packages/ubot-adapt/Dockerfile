# Збирати з кореня репо: docker build -f packages/ubot-adapt/Dockerfile .
# Копіюємо лише ubot-queue + цей пакет; pyproject фільтруємо під цей workspace.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages/ubot-queue ./packages/ubot-queue
COPY packages/ubot-adapt ./packages/ubot-adapt
COPY scripts/filter-workspace-pyproject.py ./
RUN python3 filter-workspace-pyproject.py ubot-adapt && uv lock && uv sync --package ubot-adapt --no-dev

FROM python:3.14-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["ubot-adapt"]
