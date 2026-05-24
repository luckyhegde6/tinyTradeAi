# Agent Memory

This file serves as the long-term memory for AI agents working on TinyTrade AI. Update this file whenever a significant milestone is reached, an architectural pivot is made, or a persistent blocker is identified.

## Current State
- **Phase**: Verification & Documentation.
- **Completed**: Core data fetchers (Crypto via CoinGecko, Stocks via direct NSE API), SQLite Database, AI Sentiment (Vader+TextBlob), Anomaly Detection (Z-Score), OLED screen logic, Flask API, Telegram bot structure, comprehensive Hardware diagrams, verified Wi-Fi troubleshooting logs.
- **In Progress**: Final local tests, deploying files to Orange Pi.
- **Hardware**: Orange Pi 2G-IOT (256MB RAM) successfully booted and Wi-Fi configured after resolving ALSA driver conflict.
- **Completed Milestones**: Documented complete setup tutorial with screenshots (top, bottom, pinout) and exact wpa_cli steps.

## Active Blockers
- None.


## Architectural Decisions
- **NSE Fetching**: Switched from `yfinance` to direct `requests.Session()` to avoid `pandas` memory overhead.
- **RSS Parsing**: Using `xml.etree` instead of `feedparser` to save memory.
- **Security**: Adopted Zero Trust for Telegram bot (strict `@Luckyhegde` chat ID validation).
