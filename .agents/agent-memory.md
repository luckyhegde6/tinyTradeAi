# Agent Memory

This file serves as the long-term memory for AI agents working on TinyTrade AI. Update this file whenever a significant milestone is reached, an architectural pivot is made, or a persistent blocker is identified.

## Current State
- **Phase**: Initial Setup & Implementation.
- **Completed**: Core data fetchers (Crypto via CoinGecko, Stocks via direct NSE API), SQLite Database, AI Sentiment (Vader+TextBlob), Anomaly Detection (Z-Score), OLED screen logic, Flask API, Telegram bot structure.
- **In Progress**: Writing documentation and setting up the Agentic Swarm infrastructure.
- **Hardware**: Targeting Orange Pi 2G-IOT (256MB RAM). Testing locally on Windows machine.

## Active Blockers
- None currently.

## Architectural Decisions
- **NSE Fetching**: Switched from `yfinance` to direct `requests.Session()` to avoid `pandas` memory overhead.
- **RSS Parsing**: Using `xml.etree` instead of `feedparser` to save memory.
- **Security**: Adopted Zero Trust for Telegram bot (strict `@Luckyhegde` chat ID validation).
