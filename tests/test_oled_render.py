#!/usr/bin/env python3
"""
OLED Display Rendering Test
Tests basic drawing, text, and graphics on the display.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import Image, ImageDraw, ImageFont
import time

def test_rendering():
    """Test basic rendering capabilities."""
    print("\n" + "="*60)
    print("OLED Display Rendering Test")
    print("="*60)
    
    try:
        # Initialize device
        print("\n[1/5] Initializing display...")
        serial = i2c(port=0, address=0x3C)
        device = ssd1306(serial)
        print("      ✓ Display initialized")
        
        # Test 1: Clear display
        print("\n[2/5] Testing clear command...")
        device.clear()
        print("      ✓ Display cleared")
        time.sleep(1)
        
        # Test 2: Simple text
        print("\n[3/5] Drawing text (2 sec)...")
        with canvas(device) as draw:
            draw.text((10, 10), "TinyTrade AI", fill="white")
            draw.text((10, 25), "OLED Test", fill="white")
            draw.text((10, 40), "Status: OK", fill="white")
        time.sleep(2)
        
        # Test 3: Lines and shapes
        print("\n[4/5] Drawing shapes (2 sec)...")
        with canvas(device) as draw:
            draw.rectangle([5, 5, 122, 58], outline="white")
            draw.line([0, 32, 127, 32], fill="white")
            draw.ellipse([50, 20, 77, 45], outline="white")
        time.sleep(2)
        
        # Test 4: Pattern/grid
        print("\n[5/5] Drawing pattern (2 sec)...")
        with canvas(device) as draw:
            for x in range(0, 128, 16):
                draw.line([x, 0, x, 63], fill="white", width=1)
            for y in range(0, 64, 16):
                draw.line([0, y, 127, y], fill="white", width=1)
        time.sleep(2)
        
        # Final: Display message
        print("\n" + "="*60)
        device.clear()
        with canvas(device) as draw:
            draw.text((20, 25), "Tests Passed!", fill="white")
        print("✓ All rendering tests PASSED")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ Rendering Error: {e}")
        return False


if __name__ == "__main__":
    success = test_rendering()
    if success:
        print("\n→ Ready for integration tests!")
        print("→ Run: python3 tests/test_oled_integration.py")
    else:
        print("\n✗ Rendering test failed.")
        sys.exit(1)
