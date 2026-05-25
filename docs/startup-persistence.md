# Display Startup Persistence - Implementation & Spec

## Problem

After every Orange Pi reboot, the OLED display stopped working. The `tinytrade.service` systemd daemon restarted `main.py` automatically, but the OLED module would fail to initialize because:

1. **rda_sensor race condition**: The kernel driver `rda-sensor` claims I2C address `0x3C` at boot. The unbind command in `rc.local` runs too late — the application starts before it executes.
2. **No retry in probe_oled()**: `init_displays()` tried once and gave up. If OLED init failed due to timing, the display stayed dead until a manual restart.
3. **No runtime health check**: Once OLED was marked unavailable at boot, there was no mechanism to re-probe it later when the I2C bus becomes ready.
4. **LCD init loop bug**: `_init_attempted` flag was only set in the `except` block. When `discover_lcd_address()` returned `None` (normal case — no LCD connected), the flag was never set, causing `get_lcd_device()` to re-run the entire probe cycle every 5 seconds forever.

## Solution Architecture

### Layer 1: Systemd Service (`tinytrade.service`)

- Uses `ExecStart=/opt/tinyTradeAi/scripts/startup.sh` instead of direct Python
- `Restart=always` with `RestartSec=15` (increased from 10 for I2C settle time)
- `Before=rc-local.service` to run before rc.local (which is a fallback unbind)

### Layer 2: Startup Script (`scripts/startup.sh`)

Pre-flight checks before launching the app:

| Step | Action | Why |
|------|--------|-----|
| 1 | Wait for `/dev/i2c-0` (poll up to 10s) | I2C bus may not be ready at boot |
| 2 | Unbind `rda-sensor` from `0x3C` | Free OLED address from kernel driver |
| 3 | Sleep 1s after unbind | Let I2C bus electrical state settle |
| 4 | Probe OLED via `i2cget` (3 attempts, backoff) | Verify display is reachable before app starts |
| 5 | Probe LCD via `i2cget` (1 attempt) | Non-critical — just informational |

### Layer 3: Python Display Manager (`display/manager.py`)

Three-tier resilience:

**A. Retry on init** (`init_displays()`):
- Tries OLED probe up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s)
- This handles the case where the I2C bus is still settling during app start

**B. Periodic health check** (`check_display_health()`):
- Scheduled to run every 60 seconds in main loop
- If OLED was not available: resets the OLED singleton and re-probes (up to 3 attempts)
- If OLED was available but I2C ping fails: marks as lost, resets singleton, re-probes
- Same logic for LCD: if not available, resets LCD singleton and re-probes

**C. Singleton reset helpers**:
- `_reset_oled_singleton()` — sets `oled.display._device = None` so `get_oled_device()` retries fresh
- `_reset_lcd_singleton()` — resets `_device`, `_device_bus`, `_init_attempted` in `lcd.display`

### Layer 4: LCD Probe Fix (`lcd/display.py`)

Bug fix: `_init_attempted = True` added in the `discover_lcd_address()` returns `None` path (was only in `except` block). This eliminates the infinite 5-second re-probe loop.

### Layer 5: Fallback (`/etc/rc.local`)

Duplicates the unbind command as a safety net. If the systemd service fails completely, rc.local still frees the I2C address for manual intervention.

## Files Changed

| File | Change |
|------|--------|
| `scripts/startup.sh` | **New** — pre-flight checks + app launcher |
| `scripts/tinytrade.service` | Updated to use startup.sh |
| `scripts/rc.local` | **New** — documented fallback |
| `display/manager.py` | Retry + health check + singleton reset |
| `lcd/display.py` | Fixed `_init_attempted` flag |
| `main.py` | Added `check_display_health()` to schedule |
| `scripts/_deploy_updates.py` | Updated IP, includes new files |
| `.env.example`, `_deploy.py` | Updated default IP to 0.12 |

## Efficiency Improvements

### Before (per boot cycle):
1. OLED init: 1 attempt, fail → headless forever
2. LCD probe: runs every 5s forever (~17,280 probes/day)
3. Reboot required to fix display

### After:
1. OLED init: up to 5 attempts with backoff (total ~31s window)
2. Health check: 1 I2C ping every 60s if OLED OK; full re-probe only if failed
3. LCD probe: exactly 1 attempt at boot, cached forever (`_init_attempted = True`)
4. Display auto-recovers without reboot — watchdog handles it

## Deployment

```bash
# Deploy code changes
python scripts/_deploy_updates.py

# On Orange Pi, verify service:
systemctl status tinytrade.service
journalctl -u tinytrade.service --no-pager -n 50

# Check startup log:
tail -20 /var/log/tinytrade/startup.log

# Monitor display health:
tail -f /var/log/tinytrade/DisplayManager.log
```

## Recovery Timeline After Reboot

```
T+0s    Power on / reboot
T+1s    Kernel boots, rda-sensor claims 0x3C
T+5s    systemd starts tinytrade.service
T+6s    startup.sh: wait for /dev/i2c-0
T+7s    startup.sh: unbind rda-sensor from 0x3C
T+8s    startup.sh: i2cget probe OLED (ACK)
T+9s    startup.sh: exec python main.py
T+10s   main.py: init_displays() → probe OLED OK
T+11s   main.py: boot splash displayed
T+12s   Application fully operational
```

If OLED probe fails at T+8s (race):
```
T+70s   check_display_health() fires
T+71s   Resets OLED singleton, re-probes → success
T+72s   Display recovered (no reboot needed)
```

## Orange Pi Spec Kit

### Hardware
| Component | Spec |
|-----------|------|
| **Board** | Orange Pi 2G-IOT |
| **SoC** | RDA8810 (ARM Cortex-A5 @ 1GHz) |
| **RAM** | 256MB DDR2 |
| **Storage** | 8GB eMMC + microSD |
| **Kernel** | 3.10.62-rel5.0.2+ #4 PREEMPT (Mar 2020) |
| **OS** | Debian Stretch (9) armhf |
| **I2C Bus 0** | Pins 3 (SDA) / 5 (SCL) @ 200kHz |
| **Display** | SSD1306 128x64 OLED @ 0x3C |
| **LCD (optional)** | 16x2 via PCF8574A @ 0x38 |

### I2C Address Map
| Address | Device | Driver | Status |
|---------|--------|--------|--------|
| 0x11 | FM Radio | rda_fm_radio_i2c | Kernel |
| 0x13 | Wi-Fi Core | rda_wifi_core_i2c | Kernel |
| 0x14 | Wi-Fi RF | rda_wifi_rf_i2c | Kernel |
| 0x15 | BT Core | rda_bt_core_i2c | Kernel |
| 0x16 | BT RF | rda_bt_rf_i2c | Kernel |
| 0x3C | SSD1306 OLED | rda-sensor → freed | User |
| 0x38 | PCF8574A LCD | None | User |

### Kernel Driver Conflicts
The `rda-sensor` driver auto-binds to address `0x3C` at boot, preempting the OLED. The I2C subsystem shows `UU` in `i2cdetect` when bound. Fix: unbind via sysfs or blacklist driver.

### Package List (7 total)
```
python-dotenv==0.19.2
Flask==1.1.4
requests==2.25.1
schedule==0.6.0
vaderSentiment==3.3.2
textblob==0.15.3
Pillow==6.2.2
```
No numpy, no pandas, no transformers — RAM budget ~36MB for main.py.
