# Деплой на GKE

1. Зібрати образ і запушити в Google Container Registry (або Artifact Registry):

   ```bash
   docker build -f packages/ubot-bot/Dockerfile -t gcr.io/PROJECT_ID/ubot:latest .
   docker push gcr.io/PROJECT_ID/ubot:latest
   ```

2. Оновити `image` у `deployment.yaml` на свій образ.

3. Створити секрет з токенами (краще не комітити реальні значення в `stringData`; використати `kubectl create secret` або External Secrets):

   ```bash
   kubectl create secret generic ubot-secrets \
     --from-literal=telegram-api-id=YOUR_API_ID \
     --from-literal=telegram-api-hash=YOUR_API_HASH \
     --from-literal=telegram-bot-token=YOUR_BOT_TOKEN
   ```

4. Застосувати манифести:

   ```bash
   kubectl apply -f k8s/
   ```
