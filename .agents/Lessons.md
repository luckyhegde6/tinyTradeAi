# Lessons Learned

This file tracks past mistakes and the rules derived from them to ensure the AI swarm does not repeat errors.

## Lesson 1: Memory Exhaustion (May 2026)
- **Mistake**: Initially planned to use `yfinance` for stock data.
- **Consequence**: `yfinance` imports `pandas` and `numpy` heavily, which easily exceeds 150MB of RAM upon load, causing immediate OOM (Out Of Memory) kills on the 256MB Orange Pi.
- **Rule**: NEVER use `pandas`. Use standard `requests` and Python built-in JSON/XML parsers.

## Lesson 2: I2C Hardware Mocking (May 2026)
- **Mistake**: Writing code that crashes if the OLED display is not connected.
- **Consequence**: Developers testing on Windows/Mac couldn't run the `main.py` loop because `luma.oled` threw I2C bus errors.
- **Rule**: Always wrap hardware initialization in `try/except` blocks and provide a graceful "Mock" or "Headless" fallback so the rest of the application (API, AI, Fetchers) can still run and be tested.

## Lesson 3: Orange Pi 2G-IOT Wi-Fi Setup & ALSA Conflict (May 2026)
- **Mistake**: Standard `orangepi-config` or NetworkManager configurations can trigger conflicts with `alsa-utils` (audio tools) on legacy kernels.
- **Consequence**: After configuring Wi-Fi, the device hangs completely during boot, appearing dead on both serial console and SSH.
- **Rule**: Always purge `alsa-utils` (`sudo apt-get purge --auto-remove alsa-utils`) on legacy Debian/Ubuntu server images for the Orange Pi 2G-IOT. Audio is not needed for the TinyTrade terminal, and purging this package completely resolves network-boot freezes.

## Lesson 4: PCF8574 LCD Address Variant & rda_sensor Conflict (May 2026)
- **Mistake**: Assumed every PCF8574 LCD backpack uses address 0x27 (standard PCF8574) or 0x3F (PCF8574A). The actual device used 0x38 (PCF8574A variant). Also ignored the kernel rda_sensor driver claiming 0x3C.
- **Consequence**: `i2cdetect` showed no devices at expected addresses. Required unbinding rda_sensor and scanning the full PCF8574A range (0x38-0x3F) to discover the real address.
- **Rule**: When probing PCF8574 LCDs, check ALL addresses in both ranges (0x20-0x27 for PCF8574, 0x38-0x3F for PCF8574A). Also, account for kernel drivers claiming display addresses (rda_sensor at 0x3C) by unbinding or blacklisting.

## Lesson 6: NSE AI Suggestion Symbol Collision — Prefix Namespacing (May 2026)
- **Mistake**: Added NSE indices (NIFTY, NIFTYBANK) and marquee stocks (RELIANCE, TCS) to AI signal generation without considering that multiple data sources could share the same symbol.
- **Consequence**: A marquee stock `RELIANCE` has no `market_data` table entry (it lives in `marquee_stocks`), but if one existed, the suggestion would overwrite the wrong record. No collision happened in practice, but the design was fragile.
- **Rule**: When generating AI suggestions for assets from different data sources/symbol spaces, always prefix with the source namespace (e.g., `NSE_RELIANCE`, `NSE_TCS`). Use a consistent prefix scheme: `NSE_` for NSE marquee stocks, `US_` for US stocks, bare symbols for global assets (BTC, ETH) and market-data-backed indices (NIFTY, NIFTYBANK). Strip prefixes in display code (`oled/screens.py`, `lcd/screens.py`) for clean user-facing output.

## Lesson 5: Display Lost After Reboot — Race Condition & One-Shot Init (May 2026)
- **Mistake**: `probe_oled()` and `init_displays()` had no retry logic. If the I2C bus wasn't ready or rda_sensor hadn't been unbound yet, the OLED init failed silently and permanently. The LCD module's `_init_attempted` guard flag was only set in the `except` block — when `discover_lcd_address()` returned `None` normally, the flag stayed `False`, causing an infinite re-probe loop every 5 seconds.
- **Consequence**: After every reboot, the display was lost until someone manually SSH'd in and restarted the service. The LCD auto-discovery generated ~17,280 I2C probe attempts per day.
- **Rule**: Hardware init must always have retry logic with backoff. Singleton guard flags must be set in ALL exit paths (success, failure, exception). Add a periodic health check watchdog that re-probes hardware in case of transient failures. Never assume one-shot init will succeed on embedded Linux with kernel driver conflicts.

