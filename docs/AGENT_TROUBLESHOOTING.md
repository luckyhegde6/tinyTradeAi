# Agent Troubleshooting

If an AI Agent acting on this repository gets stuck, consult this guide.

## Problem: Agent Hallucinates Libraries
- **Symptom**: The agent tries to install `pandas`, `yfinance`, or `tensorflow`.
- **Solution**: Remind the agent to read `AGENTS.md` and `.agents/rules/no-heavy-libraries.md`.

## Problem: Playwright Fails on Orange Pi
- **Symptom**: Agent tries to run `npx playwright test` on the Orange Pi, causing an Out Of Memory kill.
- **Solution**: MCP Playwright tools must ONLY be used on the developer's local machine (Windows/Mac). The Orange Pi is for production deployment only.

## Problem: Telegram Bot Ignores User
- **Symptom**: The agent tests the Telegram bot, but it drops all requests.
- **Solution**: Check `.env`. Ensure `TELEGRAM_CHAT_ID` perfectly matches the tester's Chat ID. The Zero Trust architecture drops unmatched IDs silently.
