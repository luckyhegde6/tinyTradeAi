#!/usr/bin/env python3
"""
I2C Auto-Discovery & OLED Test Script
Scans I2C bus 0 for devices, identifies SSD1306 OLED displays,
and runs automatic tests on discovered addresses.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import smbus
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from luma.core.render import canvas
except ImportError as e:
    print(f"Error: Missing dependency: {e}")
    print("Install with: pip install smbus-cffi luma.oled Pillow")
    sys.exit(1)


class I2CScanner:
    """Scans and tests I2C devices on the bus."""
    
    def __init__(self, bus_number=0):
        self.bus_number = bus_number
        self.bus = smbus.SMBus(bus_number)
        self.devices = []
        self.ssd1306_devices = []
    
    def scan_bus(self):
        """Scan I2C bus for connected devices."""
        print(f"\n{'='*60}")
        print(f"I2C Bus Scan (Bus {self.bus_number})")
        print(f"{'='*60}\n")
        
        print("Scanning I2C addresses 0x00-0x7F...\n")
        found_count = 0
        
        for addr in range(0x00, 0x80):
            try:
                # Attempt to read one byte from address
                self.bus.read_byte(addr)
                self.devices.append(addr)
                found_count += 1
                print(f"  ✓ Found device at 0x{addr:02X}")
            except (OSError, IOError):
                pass
        
        if not self.devices:
            print("  ✗ No devices found on I2C bus")
            return False
        
        print(f"\n✓ Total devices found: {found_count}")
        return True
    
    def identify_ssd1306(self):
        """Identify which devices are SSD1306 OLED displays."""
        if not self.devices:
            print("\n✗ No devices to test. Run scan_bus() first.")
            return False
        
        print(f"\n{'='*60}")
        print("SSD1306 OLED Identification")
        print(f"{'='*60}\n")
        
        print("Testing each device for SSD1306 characteristics...\n")
        found_ssd1306 = 0
        
        for addr in self.devices:
            try:
                print(f"  Testing 0x{addr:02X}...", end=" ")
                
                # Try to initialize as SSD1306
                serial = i2c(port=self.bus_number, address=addr)
                device = ssd1306(serial)
                
                # If we get here, it's likely an SSD1306
                print(f"✓ SSD1306 detected!")
                print(f"      Resolution: {device.width}x{device.height}")
                print(f"      Type: {type(device).__name__}")
                
                self.ssd1306_devices.append({
                    'address': addr,
                    'device': device,
                    'width': device.width,
                    'height': device.height
                })
                found_ssd1306 += 1
                
            except (OSError, IOError, Exception):
                print("✗ Not SSD1306 (or communication error)")
        
        if found_ssd1306 == 0:
            print("\n✗ No SSD1306 displays found")
            return False
        
        print(f"\n✓ Total SSD1306 displays found: {found_ssd1306}")
        return True
    
    def test_device(self, addr):
        """Run comprehensive tests on a single device."""
        ssd1306_info = None
        for info in self.ssd1306_devices:
            if info['address'] == addr:
                ssd1306_info = info
                break
        
        if not ssd1306_info:
            print(f"\n✗ Device 0x{addr:02X} not identified as SSD1306")
            return False
        
        device = ssd1306_info['device']
        
        print(f"\n{'='*60}")
        print(f"Testing SSD1306 at 0x{addr:02X}")
        print(f"{'='*60}\n")
        
        try:
            # Test 1: Clear
            print("[1/5] Clear display...", end=" ")
            device.clear()
            print("✓")
            time.sleep(0.5)
            
            # Test 2: Text rendering
            print("[2/5] Text rendering...", end=" ")
            with canvas(device) as draw:
                draw.text((5, 5), "TinyTrade AI", fill="white")
                draw.text((5, 20), f"Address: 0x{addr:02X}", fill="white")
                draw.text((5, 35), f"Size: {device.width}x{device.height}", fill="white")
            print("✓")
            time.sleep(1)
            
            # Test 3: Lines
            print("[3/5] Graphics (lines)...", end=" ")
            with canvas(device) as draw:
                draw.rectangle([5, 5, device.width-5, device.height-5], outline="white")
                draw.line([0, device.height//2, device.width, device.height//2], fill="white")
            print("✓")
            time.sleep(1)
            
            # Test 4: Pattern
            print("[4/5] Graphics (pattern)...", end=" ")
            with canvas(device) as draw:
                for x in range(0, device.width, 16):
                    draw.line([x, 0, x, device.height], fill="white", width=1)
            print("✓")
            time.sleep(1)
            
            # Test 5: Final message
            print("[5/5] Confirmation message...", end=" ")
            device.clear()
            with canvas(device) as draw:
                draw.text((device.width//2 - 25, device.height//2 - 5), "Test OK!", fill="white")
            print("✓")
            
            print(f"\n✓ All tests PASSED for 0x{addr:02X}")
            return True
            
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            return False
    
    def test_all_devices(self):
        """Run tests on all discovered SSD1306 devices."""
        if not self.ssd1306_devices:
            print("\n✗ No SSD1306 devices to test")
            return False
        
        print(f"\n{'='*60}")
        print("Running Tests on All Discovered Devices")
        print(f"{'='*60}")
        
        results = []
        for info in self.ssd1306_devices:
            addr = info['address']
            success = self.test_device(addr)
            results.append((addr, success))
            time.sleep(1)
        
        # Summary
        print(f"\n{'='*60}")
        print("Test Summary")
        print(f"{'='*60}\n")
        
        passed = sum(1 for _, success in results if success)
        for addr, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  0x{addr:02X}: {status}")
        
        print(f"\nTotal: {passed}/{len(results)} devices passed")
        return passed == len(results)
    
    def generate_config(self):
        """Generate config.py snippet for discovered devices."""
        if not self.ssd1306_devices:
            print("\n✗ No devices to generate config for")
            return
        
        print(f"\n{'='*60}")
        print("Generated Configuration")
        print(f"{'='*60}\n")
        
        print("Add these to config.py:\n")
        
        for info in self.ssd1306_devices:
            addr = info['address']
            print(f"# SSD1306 OLED at address 0x{addr:02X}")
            print(f"I2C_PORT = 0")
            print(f"I2C_ADDRESS = 0x{addr:02X}\n")


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("I2C Auto-Discovery & OLED Test")
    print("="*60)
    
    bus_number = 0
    
    try:
        scanner = I2CScanner(bus_number)
        
        # Step 1: Scan bus
        if not scanner.scan_bus():
            print("\n✗ No devices found on I2C bus")
            print("  Check:")
            print("    - I2C is enabled in device tree")
            print("    - Devices are connected to SDA/SCL pins")
            print("    - Pull-up resistors are present (4.7k typical)")
            return False
        
        # Step 2: Identify SSD1306 devices
        if not scanner.identify_ssd1306():
            print("\n✗ No SSD1306 displays detected")
            print("  Other I2C devices may be present:")
            for addr in scanner.devices:
                print(f"    - 0x{addr:02X}")
            return False
        
        # Step 3: Test all SSD1306 devices
        success = scanner.test_all_devices()
        
        # Step 4: Generate config
        scanner.generate_config()
        
        if success:
            print("\n" + "="*60)
            print("✓ AUTO-DISCOVERY COMPLETE")
            print("="*60)
            print("\nNext steps:")
            print("  1. Update config.py with the address above")
            print("  2. Run: python3 tests/test_oled_integration.py")
            print("="*60 + "\n")
            return True
        else:
            print("\n✗ Some tests failed. Check connections and try again.")
            return False
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
