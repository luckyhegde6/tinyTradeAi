#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lcd.display import get_lcd_device
import time


def test_integration():
    print("\n" + "="*60)
    print("LCD Integration Test")
    print("="*60)
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
        print(f"      LCD_I2C_PORT: {LCD_I2C_PORT}")
        print(f"      LCD_I2C_ADDRESS: 0x{LCD_I2C_ADDRESS:02X}")
        print(f"      LCD_COLUMNS: {LCD_COLUMNS}")
        print(f"      LCD_ROWS: {LCD_ROWS}")
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
        print("\n" + "="*60)
        print("\u2713 Integration tests PASSED")
        print("="*60)
        return True
    except ImportError as e:
        print(f"\n\u2717 Import Error: {e}")
        print("  Check that config.py and lcd/ module exist")
        return False
    except Exception as e:
        print(f"\n\u2717 Integration Error: {e}")
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
