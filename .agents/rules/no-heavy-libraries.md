# Rule: No Heavy Libraries

The Orange Pi 2G-IOT has exactly 256MB of RAM.
The OS takes about 80-100MB.
We have roughly 100MB of free RAM for our entire application.

DO NOT import:
- `pandas`
- `numpy` (except specifically for minimal array math like std_dev)
- `scipy`
- `tensorflow` / `pytorch`
- `transformers`
- Any large headless browser frameworks natively on the Pi.

Always prefer standard library implementations (`requests`, `json`, `xml.etree`, `collections.deque`).
