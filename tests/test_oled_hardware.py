#!/usr/bin/env python3
"""
OLED Hardware Detection & Initialization Test
Tests I2C bus connectivity and SSD1306 device presence before rendering.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
import time

def test_hardware():
    """Test OLED hardware presence and readiness."""
    print("\n" + "="*60)
    print("OLED Hardware Detection Test")
    print("="*60)
    
    try:
        # Test I2C connection
        print("\n[1/3] Detecting I2C device 0x3C...")
        serial = i2c(port=0, address=0x3C)
        print("      ✓ I2C device 0x3C found")
        
        # Initialize SSD1306
        print("\n[2/3] Initializing SSD1306 OLED display...")
        device = ssd1306(serial)
        print("      ✓ SSD1306 display initialized")
        
        # Check display properties
        print("\n[3/3] Verifying display properties...")
        print(f"      ✓ Display resolution: {device.width}x{device.height} pixels")
        print(f"      ✓ Device object type: {type(device).__name__}")
        
        print("\n" + "="*60)
        print("✓ All hardware tests PASSED")
        print("="*60)
        return device
        
    except OSError as e:
        print(f"\n✗ I2C Error: {e}")
        print("  Check:")
        print("    - I2C bus enabled in device tree")
        print("    - Device address 0x3C correct")
        print("    - I2C pins connected (SDA, SCL)")
        return None
        
    except Exception as e:
        print(f"\n✗ Initialization Error: {e}")
        print("  Possible causes:")
        print("    - luma.oled not installed (pip install luma.oled)")
        print("    - Python version < 3.6 (need 3.6+)")
        print("    - Missing dependencies (Pillow, smbus, RPi.GPIO)")
        return None


if __name__ == "__main__":
    device = test_hardware()
    if device:
        print("\n→ Ready for rendering tests!")
        print("→ Run: python3 tests/test_oled_render.py")
    else:
        print("\n✗ Hardware test failed. Check troubleshooting guide.")
        sys.exit(1)
