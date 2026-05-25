#!/usr/bin/env python3
import smbus, time, sys

BUS = 0
ADDR = 0x3C

bus = smbus.SMBus(BUS)

def cmd(c):
    bus.write_byte_data(ADDR, 0x00, c)
    time.sleep(0.001)

def data(d):
    bus.write_byte_data(ADDR, 0x40, d)
    time.sleep(0.0001)

def clear():
    for page in range(8):
        cmd(0xB0 + page)
        cmd(0x00)
        cmd(0x10)
        for col in range(128):
            data(0x00)

def fill():
    for page in range(8):
        cmd(0xB0 + page)
        cmd(0x00)
        cmd(0x10)
        for col in range(128):
            data(0xFF)

try:
    # Probe
    bus.read_byte(ADDR)
    print("OLED found at 0x%02X" % ADDR)
except:
    print("No OLED at 0x%02X, trying 0x3D..." % ADDR)
    ADDR = 0x3D
    try:
        bus.read_byte(ADDR)
        print("OLED found at 0x%02X" % ADDR)
    except:
        print("No OLED at either address. Check I2C.")
        bus.close()
        sys.exit(1)

print("Initializing SSD1306...")

cmd(0xAE)  # Display OFF
cmd(0xD5); cmd(0x80)  # Clock
cmd(0xA8); cmd(0x3F)  # Mux ratio
cmd(0xD3); cmd(0x00)  # Offset
cmd(0x40)  # Start line
cmd(0x8D); cmd(0x14)  # Charge pump ON
cmd(0x20); cmd(0x00)  # Memory mode
cmd(0xA1)  # Segment remap
cmd(0xC8)  # COM scan direction
cmd(0xDA); cmd(0x12)  # COM pins
cmd(0x81); cmd(0xCF)  # Contrast
cmd(0xD9); cmd(0xF1)  # Pre-charge
cmd(0xDB); cmd(0x40)  # VCOMH
cmd(0xA4)  # Resume display
cmd(0xA6)  # Normal display
cmd(0xAF)  # Display ON

time.sleep(0.1)

print("Filling screen (all white)...")
fill()
time.sleep(1)

print("Clearing screen...")
clear()
time.sleep(0.5)

print("Drawing pattern (checkerboard)...")
for page in range(8):
    cmd(0xB0 + page)
    cmd(0x00)
    cmd(0x10)
    for col in range(128):
        if (page + col // 16) % 2 == 0:
            data(0xFF)
        else:
            data(0x00)

print("OLED test complete! You should see:")
print("  1. All white (1 second)")
print("  2. Clear/blank (0.5 second)")
print("  3. Checkerboard pattern (until exit)")
print("Press CTRL+C to exit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    clear()
    cmd(0xAE)
    bus.close()
    print("Done.")
