# k8s — ubot-adapt

Деплой воркера адаптації тексту (meta-llama/Llama-3.1-8B-Instruct). **KEDA:** воркер запускається лише коли в Redis є повідомлення в черзі `ubot:adapt_tasks` (scale-to-zero).

- **nodeSelector:** `preem: "true"`
- **KEDA:** застосувати `keda-scaledobject.yaml` після deployment. Потрібен KEDA у кластері.
- Секрет `ubot-secrets`: telegram-api-id, telegram-api-hash, telegram-bot-token, redis-url, **redis-address** (host:port), **redis-password** (порожній, якщо без пароля), hf-token.
- Запуск: `kubectl apply -f deployment.yaml` та `kubectl apply -f keda-scaledobject.yaml`
