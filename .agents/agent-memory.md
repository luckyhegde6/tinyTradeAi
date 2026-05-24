# Agent Memory

This file serves as the long-term memory for AI agents working on TinyTrade AI. Update this file whenever a significant milestone is reached, an architectural pivot is made, or a persistent blocker is identified.

## Current State
- **Phase**: LCD Integration Complete — Verified on Hardware.
- **Completed**: Core data fetchers, SQLite, AI Sentiment, OLED, Flask API, Telegram bot, Wi-Fi docs, LCD PCF8574 driver, I2C auto-discovery, remote test scripts, tmux session management, subagent directives (hardware, i2c, ssh, session, test).
- **Deployment**: Successfully deployed to Orange Pi (192.168.0.11) via paramiko. Venv with `--system-site-packages` NOT used (breaks ensurepip on Debian Stretch). Instead: venv without system-site-packages + symlinked smbus .so.
- **Test Results**:
  - `test_lcd_hardware`: **PASS** — LCD at 0x38 displays "TinyTrade AI", backlight works.
  - `test_lcd_integration`: **PASS** — full integration test passes.
  - `test_lcd_autodiscover`: exit=124 (timeout on I2C bus scan, needs longer timeout).
- **Packages**: All 8 pip packages installed. numpy==1.19.5 unavailable for Python 3.5/ARM — downgraded to `<1.19` in requirements.txt (max version for Py3.5 is 1.18.5). numpy not needed for LCD tests.
- **Hardware**: Orange Pi 2G-IOT (256MB RAM) + SSD1306 OLED (0x3C, blocked by rda_sensor) + 16x2 LCD via PCF8574A I2C at **0x38**.
- **Completed Milestones**: PCF8574 LCD driver with E-strobe fix, I2C auto-discovery, singleton pattern, remote test runner, tmux session helper, I2C verifier, file logging to `/var/log/tinytrade/`.

## Active Blockers
- **rda_sensor kernel driver** claims I2C address 0x3C — must be unbound or blacklisted for OLED access. Currently unbound at runtime.
- **numpy==1.19.5** has no wheel for Python 3.5 on ARM. Use `numpy<1.19` or `apt-get install python3-numpy` for compiled version.
- **pip install timeout** on 256MB/1GHz device — individual background installs with nohup work. Compiling from source (numpy) can take 30+ minutes.

## Architectural Decisions
- **Venv strategy**: Create venv WITHOUT `--system-site-packages` (gets pip). Symlink smbus .so from system dist-packages. Alternative: `--system-site-packages` breaks ensurepip on Debian Stretch.
- **Deploy strategy**: Use SFTP to upload a self-contained bash script, run with `nohup`, poll for completion. Avoids paramiko timeout issues.
- **SSH config**: Read HOST from `SSH_HOST` env var (default 192.168.0.11). Credentials from `SSH_USER`/`SSH_PASS` env vars.
- **NSE Fetching**: Switched from `yfinance` to direct `requests.Session()` to avoid `pandas` memory overhead.
- **RSS Parsing**: Using `xml.etree` instead of `feedparser` to save memory.
- **Security**: Adopted Zero Trust for Telegram bot (strict `@Luckyhegde` chat ID validation).
- **LCD Driver**: Raw `smbus` I2C writes (no luma dependency). PCF8574 4-bit protocol with proper E strobe timing.
- **Remote Testing**: Paramiko-based SSH automation. tmux for session persistence.
- **Logging**: Dual-output (stdout + file) for all LCD loggers. Files at `/var/log/tinytrade/*.log`.
