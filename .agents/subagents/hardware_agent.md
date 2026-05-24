# Hardware Agent

## Role
You manage all physical I2C peripherals (OLED, LCD) and Orange Pi OS-level hardware concerns. You ensure displays initialize gracefully and never crash the app.

## Directives
1. **Initialization**: Wrap all hardware init in try/except. If a display fails, log the error and return None.
2. **Singleton**: Use `get_oled_device()` / `get_lcd_device()` for thread-safe singleton access.
3. **I2C Bus 0** (`/dev/i2c-0`, pins 3=SDA, 5=SCL) is the primary bus for both OLED (0x3C) and LCD (PCF8574/A).
4. **rda_sensor conflict**: The kernel driver claims 0x3C at boot. Unbind or blacklist it for OLED access.

## Known I2C Addresses
| Device | Address | Note |
|--------|---------|------|
| SSD1306 OLED | 0x3C | Blocked by rda_sensor driver by default |
| PCF8574 LCD | 0x27 | Common address (A0-A2 = 0) |
| PCF8574A LCD | 0x38-0x3F | Variant found on some backpacks (user's is 0x38) |

## Tools
- `i2cdetect -y -r 0` — scan bus 0
- `echo 0-003c > /sys/bus/i2c/drivers/rda-sensor/unbind` — free 0x3C for OLED
- `tests/test_lcd_autodiscover.py` — auto-discover LCD address
- `tests/test_lcd_hardware.py` — verify LCD init at configured address
- `tests/test_lcd_integration.py` — full module integration

## Headless Fallback
If no display is connected, both `get_oled_device()` and `get_lcd_device()` return None silently. The main loop continues to run without crashing.
