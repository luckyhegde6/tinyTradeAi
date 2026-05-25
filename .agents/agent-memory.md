# Agent Memory

This file serves as the long-term memory for AI agents working on TinyTrade AI. Update this file whenever a significant milestone is reached, an architectural pivot is made, or a persistent blocker is identified.

## Current State
- **Phase**: NSE AI Suggestions Complete — signal generator now covers NSE indices (NIFTY, NIFTYBANK) + top 10 marquee stocks (as NSE_RELIANCE, NSE_TCS, etc.). OLED cycles 55 screens when both NSE+US markets open.
- **Completed**: Core data fetchers, SQLite, AI Sentiment, OLED, Flask API, Telegram bot, LCD PCF8574 driver, I2C auto-discovery, remote test scripts, display manager, subagent directives, boot splash with IP, NSE API rewrite with cache and market hours, NSE AI signals with symbol prefix namespacing (NSE_), 55-screen OLED rotation.
- **Deployment**: Running on Orange Pi (192.168.0.11) via nohup. Default SSH_HOST updated to 0.11 in `_deploy.py` and `.env.example`. Venv without `--system-site-packages`.
- **Display Manager** (`display/manager.py`): Unified init that probes OLED via `oled/display.py` (falls back from luma.oled to `simple_driver.SSD1306`) and LCD via `lcd/display.py`. Routes render calls to both. Main event loop renders every 5s.
- **OLED Driver Fixes** (`oled/simple_driver.py`):
  - **Bug 1**: Used `write_byte` instead of `write_byte_data(addr, 0x00, cmd)` for init commands. Fix: proper control byte.
  - **Bug 2**: Used PIL `tobytes()` which packs pixels horizontally, but SSD1306 expects vertical 8-pixel columns. Fix: pixel-by-pixel vertical byte packing.
- **Python 3.5 Compatibility**: All f-strings replaced with % formatting across entire codebase (15+ files affected).
- **numpy removed**: `ai/anomaly.py` replaced numpy with pure Python `math.sqrt()` for Z-score calculation. Eliminates numpy dependency entirely.
- **SQLite 3.16 Compat**: `update_market_data` changed from `ON CONFLICT ... DO UPDATE SET` (requires 3.24+) to manual SELECT-then-INSERT/UPDATE.
- **Test Results**:
  - `simple_driver` OLED test: **PASS** — clear text visible on display.
  - OLED application screens: **WORKING** — content cycling (crypto → sentiment → alerts → stocks).
  - LCD at 0x38: **NON-RESPONSIVE** — EPERM on writes. Display manager caches failure (`_init_attempted` flag) to avoid retry loops.
- **I2C Bus Details**: bus 0 = internal RDA I2C, bus 1 = rda-i2c.1 @400kHz, bus 2 = rda-i2c.2 @200kHz.
- **Kernel I2C Drivers**: rda_bt_core_i2c (0x15), rda_bt_rf_i2c (0x16), rda_fm_radio_i2c (0x11), rda_wifi_core_i2c (0x13), rda_wifi_rf_i2c (0x14). rda-sensor loaded but no devices bound. None claim 0x38 or 0x3C.
- **Hardware**: Orange Pi 2G-IOT (256MB RAM) + SSD1306 OLED at 0x3C (working with simple_driver) + 16x2 LCD via PCF8574A at 0x38 (non-responsive).
- **Packages**: 7 pip packages installed (numpy removed from requirements). Pillow 6.2.2, Flask, requests, etc.

## Active Blockers
- **LCD PCF8574 at 0x38**: Non-responsive (no ACK). Physical connection likely bad or backpack lost power between sessions.
- **pip install timeout** on 256MB/1GHz device — individual background installs with nohup work.
- **Python 3.5.3 blocks security fixes**: All 8 Dependabot CVEs require package versions that dropped Python 3.5 support. Fix requires upgrading to Python 3.7+ via backports, compilation, or OS upgrade to Debian 10. See `docs/python-upgrade.md`.

## Resolved Blockers

## Resolved Blockers
- **rda_sensor rebinds to 0x3C on every boot**: Now handled by startup.sh with 1s settle delay, systemd tinytrade.service with `Before=rc-local.service`, and fallback in rc.local.
- **Display lost after reboot**: Fixed with 3-layer approach:
  1. `startup.sh` — waits for I2C bus, unbinds rda_sensor, probes OLED with 3-attempt backoff
  2. `display/manager.py` — 5-attempt exponential backoff in init + health check watchdog every 60s
  3. `lcd/display.py` — `_init_attempted` flag fixed to prevent infinite 5s re-probe loop

## Architectural Decisions
- **Venv strategy**: Create venv WITHOUT `--system-site-packages` (gets pip). Symlink smbus .so from system dist-packages. Alternative: `--system-site-packages` breaks ensurepip on Debian Stretch.
- **Deploy strategy**: Use SFTP to upload a self-contained bash script, run with `nohup`, poll for completion. Avoids paramiko timeout issues.
- **SSH config**: Read HOST from `SSH_HOST` env var (default 192.168.0.12). Credentials from `SSH_USER`/`SSH_PASS` env vars.
- **NSE Fetching**: Switched from `yfinance` to direct `requests.Session()` to avoid `pandas` memory overhead.
- **RSS Parsing**: Using `xml.etree` instead of `feedparser` to save memory.
- **Security**: Adopted Zero Trust for Telegram bot (strict `@Luckyhegde` chat ID validation).
- **LCD Driver**: Raw `smbus` I2C writes (no luma dependency). PCF8574 4-bit protocol with proper E strobe timing.
- **Remote Testing**: Paramiko-based SSH automation. tmux for session persistence.
- **Logging**: Dual-output (stdout + file) for all LCD loggers. Files at `/var/log/tinytrade/*.log`.
- **API Framework**: Flask (not FastAPI) — Python 3.5.3 on Debian Stretch precludes FastAPI/uvicorn which require 3.6+. 9 endpoints in `api/app.py` covering status, prices, sentiment, alerts, config CRUD, display control, and system restart.
- **Runtime Config**: `utils/config_manager.py` — JSON file-backed (`runtime_config.json`), thread-safe with RLock. Supports live updates via PUT `/api/config` without restart.
- **Display Control**: `/api/display/screen/oled` and `/api/display/screen/lcd` endpoints allow forcing screen index remotely. Used for debugging or manual override.
- **System Restart**: `/api/system/restart` sets a flag checked by main loop, then `os._exit(0)` after 1s. Systemd `Restart=always` respawns the service.
