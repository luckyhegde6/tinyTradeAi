# Rule: Zero Trust

All external integrations MUST adhere to Zero Trust principles.

1. **Telegram**: Do not trust any incoming message. Before parsing the command, verify the `chat_id` strictly matches the `TELEGRAM_CHAT_ID` environment variable. If it does not, drop the message immediately without responding. Do not even send a "You are unauthorized" message, to prevent fingerprinting.
2. **Environment Variables**: Never hardcode secrets. Always use `.env`.
3. **API Endpoints**: The Flask API should only bind to `0.0.0.0` if deployed behind a firewall or reverse proxy. In raw form on the Pi, ensure no sensitive commands (like reboot) can be triggered via unauthenticated endpoints.
