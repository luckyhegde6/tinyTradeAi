#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lcd.driver import PCF8574LCD
import smbus
import time


def test_hardware():
    print("\n" + "="*60)
    print("PCF8574 LCD Hardware Detection Test")
    print("="*60)
    from config import LCD_I2C_PORT, LCD_I2C_ADDRESS
    if LCD_I2C_ADDRESS == 0x00:
        print("\n\u2717 LCD_I2C_ADDRESS is 0x00 (not configured)")
        print("  Run tests/test_lcd_autodiscover.py first")
        return None
    try:
        print(f"\n[1/3] Opening I2C bus {LCD_I2C_PORT}...")
        bus = smbus.SMBus(LCD_I2C_PORT)
        print(f"      \u2713 I2C bus {LCD_I2C_PORT} opened")
        print(f"\n[2/3] Initializing PCF8574 LCD at 0x{LCD_I2C_ADDRESS:02X}...")
        lcd = PCF8574LCD(bus, LCD_I2C_ADDRESS, 16, 2)
        print(f"      \u2713 PCF8574 LCD initialized")
        print(f"\n[3/3] Running display test...")
        lcd.clear()
        lcd.write_line("TinyTrade AI", 0)
        lcd.write_line(f"Addr: 0x{LCD_I2C_ADDRESS:02X}", 1)
        lcd.set_backlight(True)
        print(f"      \u2713 Text displayed: 'TinyTrade AI'")
        print(f"      \u2713 Backlight on")
        print(f"\n" + "="*60)
        print("\u2713 Hardware test PASSED")
        print("="*60)
        return lcd
    except OSError as e:
        print(f"\n\u2717 I2C Error: {e}")
        print("  Check:")
        print("    - I2C bus enabled in device tree")
        print(f"    - Device address 0x{LCD_I2C_ADDRESS:02X} correct")
        print("    - I2C pins connected (SDA, SCL)")
        return None
    except Exception as e:
        print(f"\n\u2717 Initialization Error: {e}")
        return None


if __name__ == "__main__":
    device = test_hardware()
    if device:
        print("\n\u2192 Ready for integration test!")
        print("\u2192 Run: python3 tests/test_lcd_integration.py")
        try:
            input("\nPress Enter to clear display and exit...")
            device.clear()
            device.set_backlight(False)
            device.close()
        except Exception:
            pass
    else:
        print("\n\u2717 Hardware test failed.")
        sys.exit(1)
