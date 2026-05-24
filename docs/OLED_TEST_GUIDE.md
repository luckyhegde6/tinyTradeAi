# OLED Integration Test Guide

## Overview

### Quick Path (Recommended for First-Time Setup)
Run **Auto-Discovery** first if you don't know the I2C address:
```bash
python3 tests/test_oled_autodiscover.py
```
This will scan the I2C bus, identify SSD1306 displays, run tests, and generate config.

### Standard Three-Stage Pipeline
If you already know the I2C address, run:

1. **Hardware Test** — I2C bus and device detection
2. **Rendering Test** — Display drawing and graphics
3. **Integration Test** — Project module integration and singleton pattern

## Prerequisites

```bash
# Ensure Python 3.7+ is installed
python3 --version

# Activate virtual environment
cd /opt/tinyTradeAi
source venv/bin/activate

# Verify dependencies are installed
pip list | grep luma
# Should show: luma-oled, Pillow, etc.
```

## Stage 1: Hardware Test

**Purpose:** Verify I2C connection and SSD1306 device presence.

**Command:**
```bash
python3 tests/test_oled_hardware.py
```

**Note:** This test uses hardcoded address 0x3C. If your device is at a different address, use auto-discovery first.

---

## Auto-Discovery (NEW - Recommended for Unknown Addresses)

**Purpose:** Automatically scan I2C bus, identify SSD1306 devices, and run tests on all discovered addresses.

**Command:**
```bash
python3 tests/test_oled_autodiscover.py
```

**Features:**
- ✓ Scans entire I2C bus (0x00-0x7F)
- ✓ Identifies SSD1306 OLED displays
- ✓ Runs tests on each discovered device
- ✓ Generates config.py snippet with correct address
- ✓ Detects multiple OLED devices

**Expected Output:**
```
============================================================
I2C Auto-Discovery & OLED Test
============================================================

============================================================
I2C Bus Scan (Bus 0)
============================================================

Scanning I2C addresses 0x00-0x7F...

  ✓ Found device at 0x3C
  ✓ Found device at 0x68

✓ Total devices found: 2

============================================================
SSD1306 OLED Identification
============================================================

Testing each device for SSD1306 characteristics...

  Testing 0x3C... ✓ SSD1306 detected!
      Resolution: 128x64
      Type: ssd1306
  Testing 0x68... ✗ Not SSD1306 (or communication error)

✓ Total SSD1306 displays found: 1

============================================================
Testing SSD1306 at 0x3C
============================================================

[1/5] Clear display... ✓
[2/5] Text rendering... ✓
[3/5] Graphics (lines)... ✓
[4/5] Graphics (pattern)... ✓
[5/5] Confirmation message... ✓

✓ All tests PASSED for 0x3C

============================================================
Generated Configuration
============================================================

Add these to config.py:

# SSD1306 OLED at address 0x3C
I2C_PORT = 0
I2C_ADDRESS = 0x3C

============================================================
✓ AUTO-DISCOVERY COMPLETE
============================================================

Next steps:
  1. Update config.py with the address above
  2. Run: python3 tests/test_oled_integration.py
============================================================
```

**When to Use Auto-Discovery:**
- First time setup with unknown I2C address
- Multiple OLED devices on same bus
- Address changed or reconfigured
- Troubleshooting address conflicts

**Troubleshooting Auto-Discovery:**

| Issue | Cause | Solution |
|-------|-------|----------|
| No devices found | I2C bus disabled or no devices connected | Enable I2C, check connections |
| No SSD1306 found | Device is different type | Check other I2C addresses listed |
| Test fails on discovered address | Device communication error | Check I2C pull-ups, cable quality |

---

## Stage 1: Hardware Test (with Known Address)

**Expected Output:**
```
============================================================
OLED Hardware Detection Test
============================================================

[1/3] Detecting I2C device 0x3C...
      ✓ I2C device 0x3C found

[2/3] Initializing SSD1306 OLED display...
      ✓ SSD1306 display initialized

[3/3] Verifying display properties...
      ✓ Display resolution: 128x64 pixels
      ✓ Device object type: ssd1306

============================================================
✓ All hardware tests PASSED
============================================================

→ Ready for rendering tests!
→ Run: python3 tests/test_oled_render.py
```

**Troubleshooting Hardware Test:**

| Error | Cause | Solution |
|-------|-------|----------|
| `OSError: [Errno 121] Remote I/O error` | I2C device not found | Check I2C pins (SDA/SCL), address, or enable I2C in device tree |
| `ModuleNotFoundError: No module named 'luma'` | luma.oled not installed | `pip install --no-cache-dir luma.oled` |
| `OSError: [Errno 2] No such file or directory: '/dev/i2c-0'` | I2C bus not available | Enable I2C in device tree or check device |

---

## Stage 2: Rendering Test

**Purpose:** Verify display can render text, lines, and shapes.

**Command:**
```bash
python3 tests/test_oled_render.py
```

**Expected Output:**
```
============================================================
OLED Display Rendering Test
============================================================

[1/5] Initializing display...
      ✓ Display initialized

[2/5] Testing clear command...
      ✓ Display cleared

[3/5] Drawing text (2 sec)...
[display shows: TinyTrade AI / OLED Test / Status: OK]

[4/5] Drawing shapes (2 sec)...
[display shows: rectangle, line, ellipse]

[5/5] Drawing pattern (2 sec)...
[display shows: grid pattern]

============================================================
✓ All rendering tests PASSED
============================================================

→ Ready for integration tests!
→ Run: python3 tests/test_oled_integration.py
```

**Visual Verification:**
- Text should appear crisp and readable on physical display
- Shapes should be clearly drawn
- Display should clear between each test without residual pixels
- Pattern should show regular grid without distortion

**Troubleshooting Rendering Test:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Display stays blank | Device not initialized | Go back to Hardware Test |
| Garbled/corrupted display | I2C noise or weak connection | Check I2C pull-up resistors, shorten cables |
| Text appears but distorted | Contrast issue | May be normal, proceed to integration test |
| Display times out/hangs | I2C bus stuck | Restart device and retry |

---

## Stage 3: Integration Test

**Purpose:** Verify module integration, singleton pattern, and config loading.

**Command:**
```bash
python3 tests/test_oled_integration.py
```

**Expected Output:**
```
============================================================
OLED Integration Test
============================================================

[1/4] Testing singleton pattern...
      ✓ Singleton pattern working (same object)

[2/4] Verifying configuration...
      I2C_PORT: 0
      I2C_ADDRESS: 0x3C
      ✓ Configuration loaded

[3/4] Rendering project content (3 sec)...
[display shows trading-style content]

[4/4] Clearing display...
      ✓ Display cleared

============================================================
✓ Integration tests PASSED
============================================================

✓ OLED module ready for production!
→ You can now integrate the display into the main application

Example:
  from oled.display import get_oled_device
  from luma.core.render import canvas
  device = get_oled_device()
  if device:
      with canvas(device) as draw:
          draw.text((0, 0), 'Your content', fill='white')
```

**Troubleshooting Integration Test:**

| Error | Cause | Solution |
|-------|-------|----------|
| `ImportError: No module named 'config'` | config.py missing | Ensure config.py exists in project root |
| `ImportError: No module named 'oled'` | oled module not found | Check oled/display.py exists |
| Singleton test fails | Device creation error | Check Hardware and Rendering tests first |

---

## Full Test Suite (Sequential)

Run auto-discovery + all tests in sequence:

```bash
#!/bin/bash
# Complete OLED setup and test suite

echo "Running OLED auto-discovery and test suite..."
source venv/bin/activate

echo -e "\n=== Stage 0: Auto-Discovery ==="
python3 tests/test_oled_autodiscover.py || { echo "Auto-discovery failed!"; exit 1; }

# User should update config.py with discovered address
echo -e "\n⚠️  Update config.py with I2C_ADDRESS from above, then continue"
read -p "Press Enter when config.py is updated..."

echo -e "\n=== Stage 1: Hardware ==="
python3 tests/test_oled_hardware.py || { echo "Hardware test failed!"; exit 1; }

echo -e "\n=== Stage 2: Rendering ==="
python3 tests/test_oled_render.py || { echo "Rendering test failed!"; exit 1; }

echo -e "\n=== Stage 3: Integration ==="
python3 tests/test_oled_integration.py || { echo "Integration test failed!"; exit 1; }

echo -e "\n✓ All tests passed! OLED ready for production."
```

Save as `scripts/run_oled_full_setup.sh` and run:
```bash
bash scripts/run_oled_full_setup.sh
```

---

## Production Integration

Once all tests pass, integrate into main application:

```python
# In main.py or other modules
from oled.display import get_oled_device
from luma.core.render import canvas
import time

def update_display(data):
    """Update display with trading data."""
    device = get_oled_device()
    if not device:
        print("Display not available, running headless")
        return
    
    with canvas(device) as draw:
        draw.text((5, 5), f"BTC: ${data['btc_price']}", fill="white")
        draw.text((5, 20), f"Trend: {data['trend']}", fill="white")
        draw.text((5, 35), f"Alert: {data['alert']}", fill="white")

# Safe headless operation if display fails
if __name__ == "__main__":
    trading_data = {
        'btc_price': '45,230',
        'trend': 'UP +2.5%',
        'alert': 'Active'
    }
    update_display(trading_data)
```

---

## Performance Expectations

| Test | Duration | Expected Behavior |
|------|----------|-------------------|
| Hardware | < 1 sec | I2C probe + device init |
| Rendering | ~10 sec | 5 render cycles with delays |
| Integration | ~3 sec | Singleton check + config load |
| Total | ~15 sec | All stages sequential |

---

## Related Documentation
- [oled/README.md](../oled/README.md) - OLED module overview
- [docs/PYTHON_UPGRADE.md](../docs/PYTHON_UPGRADE.md) - Python 3.7 setup
- [docs/ORANGE_PI_SETUP.md](../docs/ORANGE_PI_SETUP.md) - Device configuration

## Quick Reference

| Task | Command |
|------|---------|
| Find I2C address | `python3 tests/test_oled_autodiscover.py` |
| Test known address | `python3 tests/test_oled_hardware.py` |
| Test display rendering | `python3 tests/test_oled_render.py` |
| Test module integration | `python3 tests/test_oled_integration.py` |
| Full setup (auto → tests) | `bash scripts/run_oled_full_setup.sh` |
