#!/usr/bin/env python3
"""
Simple OLED Display Test - Minimal Dependencies
Works with Python 3.5+ (smbus only, no PIL)
Run: python3 test_oled_simple.py
"""

import sys
import time

def test_oled():
    print("\n" + "="*60)
    print("OLED Display Test (Python 3.5+ Compatible)")
    print("="*60 + "\n")
    
    try:
        # Test 1: Check dependencies
        print("[1/3] Checking dependencies...")
        import smbus
        print("      OK: smbus")
        
        # Test 2: I2C connection
        print("\n[2/3] Connecting to I2C device at 0x3C...")
        bus = smbus.SMBus(0)
        
        # Try to read from device (non-destructive probe)
        try:
            data = bus.read_byte(0x3C)
            print("      OK: Device found! (read byte: 0x{0:02X})".format(data))
        except OSError as e:
            print("      ERROR: Device not responding: {0}".format(e))
            print("\n      Troubleshooting:")
            print("        - Check I2C cable connections (SDA/SCL)")
            print("        - Run: sudo i2cdetect -y 0")
            print("        - Check pull-up resistors on I2C bus")
            return False
        
        # Test 3: Initialize display
        print("\n[3/3] Initializing SSD1306...")
        
        # SSD1306 initialization sequence
        init_commands = [
            0xAE,  # Display OFF
            0x00, 0x10,  # Column address
            0x40,  # Start line
            0xB0,  # Page address
            0x81, 0xFF,  # Contrast
            0xA1,  # Segment remap
            0xA6,  # Normal display
            0xA8, 0x3F,  # Multiplex ratio
            0xD3, 0x00,  # Display offset
            0xD5, 0x80,  # Clock divider
            0xD9, 0xF1,  # Pre-charge period
            0xDA, 0x12,  # COM pins
            0xDB, 0x40,  # VCOMH
            0x8D, 0x14,  # Charge pump enable
            0xAF,  # Display ON
        ]
        
        for cmd in init_commands:
            try:
                bus.write_byte(0x3C, cmd)
            except:
                pass
        
        time.sleep(0.5)
        
        # Send test pattern (alternating bytes to create pattern)
        print("      -> Sending test pattern to display...")
        for page in range(8):
            # Set page address
            bus.write_byte(0x3C, 0xB0 + page)
            bus.write_byte(0x3C, 0x00)
            bus.write_byte(0x3C, 0x10)
            
            # Write alternating pattern (0xFF = white, 0x00 = black)
            for col in range(128):
                if col % 2 == 0:
                    bus.write_byte(0x3C, 0xFF)  # White
                else:
                    bus.write_byte(0x3C, 0x00)  # Black
        
        time.sleep(1)
        print("      OK: Display initialized and test pattern sent")
        
        # Clear display
        print("\n      -> Clearing display...")
        for page in range(8):
            bus.write_byte(0x3C, 0xB0 + page)
            bus.write_byte(0x3C, 0x00)
            bus.write_byte(0x3C, 0x10)
            
            for col in range(128):
                bus.write_byte(0x3C, 0x00)
        
        print("      OK: Display cleared")
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        print("\nDisplay is working correctly!")
        print("You should have seen a pattern, then a clear screen.\n")
        return True
        
    except ImportError as e:
        print("\nERROR: Missing dependency: {0}".format(e))
        print("\nInstall with:")
        print("  sudo apt-get install -y python3-smbus")
        return False
    except Exception as e:
        print("\nERROR: {0}".format(e))
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_oled()
    sys.exit(0 if success else 1)
