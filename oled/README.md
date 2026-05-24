# OLED Display Integration Guide

## Overview
This directory contains the SSD1306 OLED display driver for TinyTrade AI. The display runs on I2C bus 0 at address 0x3C and provides real-time trading data visualization on the Orange Pi 2G-IOT embedded device.

## File Structure
- `display.py` - Core OLED device initialization and singleton pattern
- `screens.py` - Trading screen layouts and content rendering
- `animations.py` - Animations and transitions for display updates
- `../tests/test_oled.py` - Integration and functionality tests

## Hardware Requirements
- SSD1306 OLED display (128x64 pixels)
- I2C bus 0 connection
- Device address: 0x3C (standard for SSD1306)

## Software Requirements
- Python 3.7+ (see `docs/PYTHON_UPGRADE.md` for upgrade instructions)
- luma.oled >= 3.8.0
- Pillow >= 10.0.0
- Virtual environment with project dependencies

## Quick Start

### 1. Install Dependencies
```bash
cd /opt/tinyTradeAi
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
```

### 2. Test Hardware Connection
```bash
python3 tests/test_oled_hardware.py
```

Expected output:
```
✓ I2C device 0x3C found
✓ SSD1306 display initialized
✓ Display resolution: 128x64 pixels
```

### 3. Test Display Rendering
```bash
python3 tests/test_oled_render.py
```

### 4. Run Full Integration Test
```bash
python3 tests/test_oled_integration.py
```

## Configuration

Edit `config.py` to customize:
```python
I2C_PORT = 0          # I2C bus number
I2C_ADDRESS = 0x3C    # SSD1306 device address
```

## Troubleshooting

### Display Not Detected
```bash
# Check I2C bus detection
sudo i2cdetect -r -y 0

# Try read-mode detection (compatible with SSD1306)
sudo i2cget -y 0 0x3c 0x00
```

Expected i2cget output: `0x43` (or similar byte value)

### Python/pip Issues
If you see "ModuleNotFoundError: No module named 'luma'":
1. Verify Python 3.7+: `python3 --version`
2. Activate venv: `source venv/bin/activate`
3. Reinstall: `pip install --no-cache-dir luma.oled`

### Display Garbled or Not Responding
- Verify I2C pins (SDA, SCL) connected correctly
- Check pull-up resistors on I2C lines
- Try the hardware test: `python3 tests/test_oled_hardware.py`

## Integration with Main Application

The `display.py` module provides a singleton pattern for safe multi-threaded access:

```python
from oled.display import get_oled_device
from luma.core.render import canvas

device = get_oled_device()
if device:
    with canvas(device) as draw:
        draw.text((0, 0), "Trading Data", fill="white")
```

If the display is not available, `get_oled_device()` returns None (headless mode).

## Performance Notes
- Display updates should be throttled to 1-2 Hz to avoid excessive I2C traffic
- Use buffering for multi-line renders
- See `animations.py` for efficient screen transitions

## Related Documentation
- [docs/PYTHON_UPGRADE.md](../docs/PYTHON_UPGRADE.md) - Python 3.7 compilation guide
- [docs/AGENT_TROUBLESHOOTING.md](../docs/AGENT_TROUBLESHOOTING.md) - General troubleshooting
- [docs/ORANGE_PI_SETUP.md](../docs/ORANGE_PI_SETUP.md) - Device setup
