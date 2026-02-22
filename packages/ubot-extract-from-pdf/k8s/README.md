# k8s — ubot-extract-from-pdf

Деплой воркера експорту тексту з PDF (PyMuPDF). **KEDA:** воркер запускається лише коли в Redis є повідомлення в черзі `ubot:tasks` (scale-to-zero).

- **nodeSelector:** `gpu: l4`
- **nodeAffinity:** `gpu = l4` (required)
- **KEDA:** застосувати `keda-scaledobject.yaml` після deployment. Потрібен KEDA у кластері.
- Секрет `ubot-secrets`: telegram-api-id, telegram-api-hash, telegram-bot-token, redis-url, **redis-address** (host:port, напр. `redis:6379`), **redis-password** (порожній рядок, якщо Redis без пароля).
- Запуск: `kubectl apply -f deployment.yaml` та `kubectl apply -f keda-scaledobject.yaml`
