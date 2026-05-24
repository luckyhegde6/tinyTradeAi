#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lcd.display import get_lcd_device
import time


def test_integration():
    sep = "=" * 60
    print("\n%s" % sep)
    print("LCD Integration Test")
    print("%s" % sep)
    try:
        print("\n[1/4] Testing singleton pattern...")
        device1 = get_lcd_device()
        device2 = get_lcd_device()
        if device1 is device2:
            print("      \u2713 Singleton pattern working (same object)")
        else:
            print("      \u2717 Singleton pattern failed")
            return False
        if device1 is None:
            print("      \u2717 No LCD device available (headless mode)")
            return False
        print("\n[2/4] Verifying configuration...")
        from config import LCD_I2C_PORT, LCD_I2C_ADDRESS, LCD_COLUMNS, LCD_ROWS
        print("      LCD_I2C_PORT: %d" % LCD_I2C_PORT)
        print("      LCD_I2C_ADDRESS: 0x%02X" % LCD_I2C_ADDRESS)
        print("      LCD_COLUMNS: %d" % LCD_COLUMNS)
        print("      LCD_ROWS: %d" % LCD_ROWS)
        print("      \u2713 Configuration loaded")
        print("\n[3/4] Rendering project content...")
        device1.clear()
        device1.write_line("TinyTrade AI", 0)
        device1.write_line("Integration OK", 1)
        time.sleep(2)
        device1.write_line("BTC: $45,230  ", 0)
        device1.write_line("Trend: UP +2%", 1)
        time.sleep(2)
        print("      \u2713 Content rendered")
        print("\n[4/4] Clearing display...")
        device1.clear()
        print("      \u2713 Display cleared")
        print("\n%s" % sep)
        print("\u2713 Integration tests PASSED")
        print("%s" % sep)
        return True
    except ImportError as e:
        print("\n\u2717 Import Error: %s" % e)
        print("  Check that config.py and lcd/ module exist")
        return False
    except Exception as e:
        print("\n\u2717 Integration Error: %s" % e)
        return False


if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n\u2713 LCD module ready for production!")
        print("Example:")
        print("  from lcd.display import get_lcd_device")
        print("  device = get_lcd_device()")
        print("  if device:")
        print("      device.write_line('Hello', 0)")
    else:
        print("\n\u2717 Integration test failed. Fix hardware test first.")
        sys.exit(1)
