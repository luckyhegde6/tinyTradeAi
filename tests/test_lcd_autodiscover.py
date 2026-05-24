#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import smbus
    from lcd.driver import PCF8574LCD, I2C_LCD_KNOWN_ADDRESSES
except ImportError as e:
    print(f"Error: Missing dependency: {e}")
    print("Install with: pip install smbus-cffi")
    sys.exit(1)


def scan_bus(bus_number=0):
    bus = smbus.SMBus(bus_number)
    found = []
    print(f"\n{'='*60}")
    print(f"I2C Bus Scan (Bus {bus_number})")
    print(f"{'='*60}\n")
    print("Scanning I2C addresses 0x03-0x77...\n")
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found.append(addr)
            print(f"  \u2713 Found device at 0x{addr:02X}")
        except (OSError, IOError):
            pass
    bus.close()
    if not found:
        print("  \u2717 No devices found on I2C bus")
        return []
    print(f"\n\u2713 Total devices found: {len(found)}")
    return found


def find_lcd(bus_number, candidates):
    bus = smbus.SMBus(bus_number)
    found_lcds = []
    search_order = I2C_LCD_KNOWN_ADDRESSES + [a for a in candidates if a not in I2C_LCD_KNOWN_ADDRESSES]
    print(f"\n{'='*60}")
    print("PCF8574 LCD Identification")
    print(f"{'='*60}\n")
    print(f"Testing {len(candidates)} device(s) for PCF8574 LCD...\n")
    for addr in search_order:
        if addr not in candidates:
            continue
        try:
            print(f"  Testing 0x{addr:02X}...", end=" ")
            lcd = PCF8574LCD(bus, addr, 16, 2)
            lcd.clear()
            lcd.write_line("LCD Test OK", 0)
            lcd.write_line(f"Addr: 0x{addr:02X}", 1)
            lcd.set_backlight(True)
            found_lcds.append(addr)
            print(f"\u2713 PCF8574 LCD detected!")
            print(f"      Size: 16x2 | Bus: {bus_number}")
        except Exception:
            print(f"\u2717 Not PCF8574 LCD (or comm error)")
    bus.close()
    if not found_lcds:
        print("\n\u2717 No PCF8574 LCD displays found")
        return []
    print(f"\n\u2713 Total PCF8574 LCD displays found: {len(found_lcds)}")
    return found_lcds


def print_config(addresses, bus_number):
    print(f"\n{'='*60}")
    print("Generated Configuration")
    print(f"{'='*60}\n")
    print("Add these to config.py:\n")
    for addr in addresses:
        print(f"# PCF8574 LCD at address 0x{addr:02X}")
        print(f"LCD_I2C_PORT = {bus_number}")
        print(f"LCD_I2C_ADDRESS = 0x{addr:02X}\n")


def main():
    print("\n" + "="*60)
    print("I2C PCF8574 LCD Auto-Discovery")
    print("="*60)
    bus_number = 0
    devices = scan_bus(bus_number)
    if not devices:
        print("\n  Check:")
        print("    - I2C enabled (sudo orangepi-config)")
        print("    - LCD backpack connected to SDA/SCL")
        print("    - Pull-up resistors present (4.7k typical)")
        return 1
    lcd_addrs = find_lcd(bus_number, devices)
    if not lcd_addrs:
        print("\n  Other I2C devices present (not PCF8574 LCD):")
        for addr in devices:
            print(f"    - 0x{addr:02X}")
        return 1
    print_config(lcd_addrs, bus_number)
    print("="*60)
    print("\u2713 AUTO-DISCOVERY COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("  1. Set LCD_I2C_ADDRESS in config.py")
    print("  2. Run: python3 tests/test_lcd_hardware.py")
    print("="*60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
