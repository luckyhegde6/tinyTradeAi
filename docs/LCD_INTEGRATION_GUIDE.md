# LCD (PCF8574) Integration Guide

## Overview
This guide covers the 16x2 character LCD with PCF8574 I2C backpack (e.g. [Robu.in LCD1602 IIC/I2C](https://robu.in/product/lcd1602-parallel-lcd-display-with-iic-i2c-interface/)) on the Orange Pi 2G-IOT.

## Hardware Connection (I2C Bus 0)
| LCD Pin | Orange Pi Pin | Signal |
|---------|---------------|--------|
| VCC     | Pin 2 or 4 (5V) | Power — DO NOT use Pin 1 (2.8V) |
| GND     | Pin 6 (GND)     | Ground |
| SDA     | Pin 3 (I2C0 SDA) | I2C Data |
| SCL     | Pin 5 (I2C0 SCL) | I2C Clock |

## Address Detection
PCF8574 backpacks use one of two address ranges:
- **PCF8574**: 0x20-0x27 (default 0x27)
- **PCF8574A**: 0x38-0x3F (default 0x3F, but can be 0x38)

Auto-discover with:
```bash
python3 tests/test_lcd_autodiscover.py
```
Or manually:
```bash
i2cdetect -y -r 0
```

## Configuration
Edit `config.py`:
```python
LCD_I2C_PORT = 0
LCD_I2C_ADDRESS = 0x38   # Set to 0x00 for auto-discovery on every boot
LCD_COLUMNS = 16
LCD_ROWS = 2
```

## Test Pipeline
```bash
python3 tests/test_lcd_hardware.py       # Verifies I2C + init
python3 tests/test_lcd_integration.py    # Singleton + config + rendering
```

## Known Issues
1. **rda_sensor conflict**: Kernel driver claims 0x3C. If OLED isn't detected, unbind it.
2. **Ghost text**: Always use `write_line()` (which pads to 16 chars), not `write_text()`.
3. **Power brownouts**: Use a 5V/2A wall charger, not a laptop USB port.
