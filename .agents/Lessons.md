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
