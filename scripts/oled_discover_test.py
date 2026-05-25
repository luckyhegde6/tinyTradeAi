#!/usr/bin/env python3
import smbus, time, sys, os

BUS = 0

def scan_i2c():
    bus = smbus.SMBus(BUS)
    found = []
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found.append(addr)
        except:
            pass
    bus.close()
    return found

def ssd1306_cmd(bus, addr, cmd):
    bus.write_byte_data(addr, 0x00, cmd)
    time.sleep(0.001)

def ssd1306_data(bus, addr, data):
    bus.write_byte_data(addr, 0x40, data)
    time.sleep(0.0001)

def ssd1306_init(bus, addr):
    ssd1306_cmd(bus, addr, 0xAE)
    ssd1306_cmd(bus, addr, 0xD5); ssd1306_cmd(bus, addr, 0x80)
    ssd1306_cmd(bus, addr, 0xA8); ssd1306_cmd(bus, addr, 0x3F)
    ssd1306_cmd(bus, addr, 0xD3); ssd1306_cmd(bus, addr, 0x00)
    ssd1306_cmd(bus, addr, 0x40)
    ssd1306_cmd(bus, addr, 0x8D); ssd1306_cmd(bus, addr, 0x14)
    ssd1306_cmd(bus, addr, 0x20); ssd1306_cmd(bus, addr, 0x00)
    ssd1306_cmd(bus, addr, 0xA1)
    ssd1306_cmd(bus, addr, 0xC8)
    ssd1306_cmd(bus, addr, 0xDA); ssd1306_cmd(bus, addr, 0x12)
    ssd1306_cmd(bus, addr, 0x81); ssd1306_cmd(bus, addr, 0xCF)
    ssd1306_cmd(bus, addr, 0xD9); ssd1306_cmd(bus, addr, 0xF1)
    ssd1306_cmd(bus, addr, 0xDB); ssd1306_cmd(bus, addr, 0x40)
    ssd1306_cmd(bus, addr, 0xA4)
    ssd1306_cmd(bus, addr, 0xA6)
    ssd1306_cmd(bus, addr, 0xAF)

def fill(bus, addr, byte):
    for page in range(8):
        ssd1306_cmd(bus, addr, 0xB0 + page)
        ssd1306_cmd(bus, addr, 0x00)
        ssd1306_cmd(bus, addr, 0x10)
        for col in range(128):
            ssd1306_data(bus, addr, byte)

# Step 1: Scan
print("=== Scanning I2C bus %d ===" % BUS)
devices = scan_i2c()
if not devices:
    print("No I2C devices found!")
    print("Check: I2C enabled? (sudo orangepi-config)")
    print("Check: OLED connected?")
    sys.exit(1)

print("Found at: %s" % ", ".join("0x%02X" % a for a in devices))

# Step 2: Try SSD1306 at candidate addresses
candidates = [0x3C, 0x3D] + devices
tried = set()
oled_addr = None

for addr in candidates:
    if addr in tried:
        continue
    tried.add(addr)
    print("\nProbing 0x%02X for SSD1306..." % addr)
    try:
        bus = smbus.SMBus(BUS)
        # Quick test: send display off command
        ssd1306_cmd(bus, addr, 0xAE)
        time.sleep(0.05)
        # If no exception, likely an SSD1306
        print("  -> SSD1306 detected at 0x%02X!" % addr)
        oled_addr = addr
        break
    except Exception as e:
        print("  -> Not SSD1306: %s" % e)
        try:
            bus.close()
        except:
            pass

if oled_addr is None:
    print("\nNo SSD1306 OLED found on bus.")
    bus.close()
    sys.exit(1)

# Step 3: Initialize and test
print("\n=== Initializing SSD1306 at 0x%02X ===" % oled_addr)
ssd1306_init(bus, oled_addr)
time.sleep(0.2)

print("-> All white (1s)")
fill(bus, oled_addr, 0xFF)
time.sleep(1)

print("-> Black/blank (0.5s)")
fill(bus, oled_addr, 0x00)
time.sleep(0.5)

print("-> Checkerboard pattern (until CTRL+C)")
for page in range(8):
    ssd1306_cmd(bus, oled_addr, 0xB0 + page)
    ssd1306_cmd(bus, oled_addr, 0x00)
    ssd1306_cmd(bus, oled_addr, 0x10)
    for col in range(128):
        if (page + col // 16) % 2 == 0:
            ssd1306_data(bus, oled_addr, 0xFF)
        else:
            ssd1306_data(bus, oled_addr, 0x00)

print("\nOLED test running. Press CTRL+C to exit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    fill(bus, oled_addr, 0x00)
    ssd1306_cmd(bus, oled_addr, 0xAE)
    bus.close()
    print("Done.")
