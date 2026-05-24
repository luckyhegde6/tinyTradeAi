# Agent Memory

This file serves as the long-term memory for AI agents working on TinyTrade AI. Update this file whenever a significant milestone is reached, an architectural pivot is made, or a persistent blocker is identified.

## Current State
- **Phase**: LCD Integration Complete — Remote Testing & Documentation.
- **Completed**: Core data fetchers, SQLite, AI Sentiment, OLED, Flask API, Telegram bot, Wi-Fi docs, LCD PCF8574 driver, I2C auto-discovery, remote test scripts, tmux session management, subagent directives (hardware, i2c, ssh, session, test).
- **In Progress**: Final verification on Orange Pi (address 0x38 confirmed working).
- **Hardware**: Orange Pi 2G-IOT (256MB RAM) + SSD1306 OLED (0x3C, blocked by rda_sensor) + 16x2 LCD via PCF8574A I2C at **0x38**.
- **Completed Milestones**: PCF8574 LCD driver with E-strobe fix, I2C auto-discovery, singleton pattern, remote test runner (`scripts/run_remote_tests.sh`), tmux session helper (`scripts/tmux_session.sh`), I2C verifier (`scripts/verify_i2c.sh`), file logging to `/var/log/tinytrade/`.

## Active Blockers
- **rda_sensor kernel driver** claims I2C address 0x3C — must be unbound or blacklisted for OLED access.
- **PCF8574A LCD at 0x38** — variant address, not the common 0x27. Added to known addresses list.

## Architectural Decisions
- **NSE Fetching**: Switched from `yfinance` to direct `requests.Session()` to avoid `pandas` memory overhead.
- **RSS Parsing**: Using `xml.etree` instead of `feedparser` to save memory.
- **Security**: Adopted Zero Trust for Telegram bot (strict `@Luckyhegde` chat ID validation).
- **LCD Driver**: Raw `smbus` I2C writes (no luma dependency). PCF8574 4-bit protocol with proper E strobe timing.
- **Remote Testing**: Paramiko-based SSH automation for test execution. tmux for session persistence.
- **Logging**: Dual-output (stdout + file) for all LCD loggers. Files at `/var/log/tinytrade/*.log`.
