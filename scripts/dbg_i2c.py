#!/usr/bin/env python3
import smbus, time, os, sys

BUS = 0

def scan(bus):
    found = []
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found.append(addr)
        except:
            pass
    return found

def try_read(bus, addr):
    try:
        bus.read_byte(addr)
        return True
    except:
        return False

def unbind_rda(addr_str):
    path = "/sys/bus/i2c/drivers/rda-sensor/unbind"
    if not os.path.exists(path):
        print("  rda-sensor driver not found at %s" % path)
        return False
    try:
        with open(path, "w") as f:
            f.write(addr_str)
        print("  Unbound %s from rda-sensor" % addr_str)
        return True
    except Exception as e:
        print("  Failed to unbind %s: %s" % (addr_str, e))
        return False

# Check available I2C buses
print("=== I2C Buses ===")
for f in os.listdir("/dev"):
    if f.startswith("i2c-"):
        print("  Found: /dev/%s" % f)

print("\n=== Initial I2C scan (bus %d) ===" % BUS)
bus = smbus.SMBus(BUS)
devices = scan(bus)
bus.close()

if devices:
    print("Devices found: %s" % ", ".join("0x%02X" % a for a in devices))
else:
    print("No I2C devices found.")

# Check specific addresses
for addr in [0x38, 0x3C, 0x3D]:
    bus = smbus.SMBus(BUS)
    ok = try_read(bus, addr)
    print("  0x%02X: %s" % (addr, "ACK" if ok else "NACK"))
    bus.close()

# Attempt unbind of rda-sensor at 0x3C
print("\n=== Unbinding rda-sensor ===")
unbind_rda("0-003c")
unbind_rda("0-0010")
time.sleep(0.5)

# Re-scan
print("\n=== Post-unbind I2C scan (bus %d) ===" % BUS)
bus = smbus.SMBus(BUS)
devices = scan(bus)
bus.close()

if devices:
    print("Devices found: %s" % ", ".join("0x%02X" % a for a in devices))
else:
    print("No I2C devices found.")

for addr in [0x38, 0x3C, 0x3D]:
    bus = smbus.SMBus(BUS)
    ok = try_read(bus, addr)
    print("  0x%02X: %s" % (addr, "ACK" if ok else "NACK"))
    bus.close()

print("\n=== Summary ===")
print("LCD (0x38): check connections, power, pull-up resistors")
print("OLED (0x3C): check connections, power")
print("If nothing ACKs -> I2C bus issue (pull-ups, voltage, SDA/SCL)")
