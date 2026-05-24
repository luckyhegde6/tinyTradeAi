#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lcd.driver import PCF8574LCD
import smbus


def test_hardware():
    sep = "=" * 60
    print("\n%s" % sep)
    print("PCF8574 LCD Hardware Detection Test")
    print("%s" % sep)
    from config import LCD_I2C_PORT, LCD_I2C_ADDRESS
    if LCD_I2C_ADDRESS == 0x00:
        print("\n\u2717 LCD_I2C_ADDRESS is 0x00 (not configured)")
        print("  Run tests/test_lcd_autodiscover.py first")
        return None
    try:
        print("\n[1/3] Opening I2C bus %d..." % LCD_I2C_PORT)
        bus = smbus.SMBus(LCD_I2C_PORT)
        print("      \u2713 I2C bus %d opened" % LCD_I2C_PORT)
        print("\n[2/3] Initializing PCF8574 LCD at 0x%02X..." % LCD_I2C_ADDRESS)
        lcd = PCF8574LCD(bus, LCD_I2C_ADDRESS, 16, 2)
        print("      \u2713 PCF8574 LCD initialized")
        print("\n[3/3] Running display test...")
        lcd.clear()
        lcd.write_line("TinyTrade AI", 0)
        lcd.write_line("Addr: 0x%02X" % LCD_I2C_ADDRESS, 1)
        lcd.set_backlight(True)
        print("      \u2713 Text displayed: 'TinyTrade AI'")
        print("      \u2713 Backlight on")
        print("\n%s" % sep)
        print("\u2713 Hardware test PASSED")
        print("%s" % sep)
        return lcd
    except OSError as e:
        print("\n\u2717 I2C Error: %s" % e)
        print("  Check:")
        print("    - I2C bus enabled in device tree")
        print("    - Device address 0x%02X correct" % LCD_I2C_ADDRESS)
        print("    - I2C pins connected (SDA, SCL)")
        return None
    except Exception as e:
        print("\n\u2717 Initialization Error: %s" % e)
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
