#!/usr/bin/env python3
"""
OLED Full Integration Test
Tests the complete OLED module with config, singleton pattern, and project integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oled.display import get_oled_device
from luma.core.render import canvas
import time

def test_integration():
    """Test OLED module integration with project structure."""
    print("\n" + "="*60)
    print("OLED Integration Test")
    print("="*60)
    
    try:
        # Test 1: Get device via singleton
        print("\n[1/4] Testing singleton pattern...")
        device1 = get_oled_device()
        device2 = get_oled_device()
        if device1 is device2:
            print("      ✓ Singleton pattern working (same object)")
        else:
            print("      ✗ Singleton pattern failed")
            return False
        
        if device1 is None:
            print("      ✗ Device initialization failed")
            return False
        
        # Test 2: Verify config values
        print("\n[2/4] Verifying configuration...")
        from config import I2C_PORT, I2C_ADDRESS
        print(f"      I2C_PORT: {I2C_PORT}")
        print(f"      I2C_ADDRESS: 0x{I2C_ADDRESS:02X}")
        print("      ✓ Configuration loaded")
        
        # Test 3: Render project-style content
        print("\n[3/4] Rendering project content (3 sec)...")
        with canvas(device1) as draw:
            draw.text((5, 5), "TinyTrade AI", fill="white")
            draw.line([0, 15, 127, 15], fill="white")
            draw.text((5, 20), "BTC: $45,230", fill="white")
            draw.text((5, 32), "Trend: UP +2.5%", fill="white")
            draw.text((5, 44), "Alert: Active", fill="white")
        time.sleep(3)
        
        # Test 4: Graceful shutdown
        print("\n[4/4] Clearing display...")
        device1.clear()
        print("      ✓ Display cleared")
        
        print("\n" + "="*60)
        print("✓ Integration tests PASSED")
        print("="*60)
        return True
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("  Check that config.py and oled/display.py exist")
        return False
        
    except Exception as e:
        print(f"\n✗ Integration Error: {e}")
        return False


if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n✓ OLED module ready for production!")
        print("→ You can now integrate the display into the main application")
        print("\nExample:")
        print("  from oled.display import get_oled_device")
        print("  from luma.core.render import canvas")
        print("  device = get_oled_device()")
        print("  if device:")
        print("      with canvas(device) as draw:")
        print("          draw.text((0, 0), 'Your content', fill='white')")
    else:
        print("\n✗ Integration test failed. Fix hardware test first.")
        sys.exit(1)
