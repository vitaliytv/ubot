# Збирати з кореня репо: docker build -f packages/ubot-adapt/Dockerfile --build-arg HF_TOKEN=xxx .
# Копіюємо лише ubot-queue + цей пакет; pyproject фільтруємо під цей workspace.
# Debian (не Alpine): torch/transformers мають лише manylinux (glibc) wheels, на musl не працюють.
# Модель завантажується під час build, щоб не витрачати час на завантаження при запуску контейнера.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY packages/ubot-queue ./packages/ubot-queue
COPY packages/ubot-adapt ./packages/ubot-adapt
COPY scripts/filter-workspace-pyproject.py ./
RUN python3 filter-workspace-pyproject.py ubot-adapt && uv lock && uv sync --package ubot-adapt --no-dev

# Завантаження моделі з Hugging Face в кеш (meta-llama/Llama-3.1-8B-Instruct — gated, потрібен HF_TOKEN).
ARG HF_TOKEN
ENV HF_HOME=/app/.cache/huggingface
ENV HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}
RUN /app/.venv/bin/python -c "\
from transformers import AutoModelForCausalLM, AutoTokenizer;\
from ubot_adapt.adapt import MODEL_ID;\
AutoTokenizer.from_pretrained(MODEL_ID);\
AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype='auto');\
"

FROM python:3.14-slim-bookworm
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
COPY --from=builder /app/.cache /app/.cache
ENV PATH="/app/.venv/bin:$PATH"
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_OFFLINE=1
ENTRYPOINT ["ubot-adapt"]
