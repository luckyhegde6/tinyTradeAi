import smbus
import time
import sys

# Try to init LCD with RPLCD-style approach
bus = smbus.SMBus(0)
addr = 0x38
BACKLIGHT = 0x08
ENABLE = 0x04
RS = 0x01

def write_byte(val):
    bus.write_byte(addr, val)

def strobe(data):
    combined = data | ENABLE | BACKLIGHT
    write_byte(combined)
    time.sleep(0.0005)
    write_byte(combined & ~ENABLE)
    time.sleep(0.0005)

def write4bits(nibble):
    val = (nibble << 4) & 0xF0
    strobe(val)

def send_byte(byte, rs_mode=0):
    high = (byte & 0xF0) | rs_mode
    low = ((byte << 4) & 0xF0) | rs_mode
    strobe(high)
    time.sleep(0.0001)
    strobe(low)
    time.sleep(0.0001)

def write_cmd(cmd):
    send_byte(cmd, 0)

def write_char(ch):
    send_byte(ord(ch), RS)

def write_text(text):
    for ch in str(text):
        write_char(ch)

print("Starting raw LCD init...")

# Power-up: set all pins low, backlight on
write_byte(0x00)
time.sleep(0.05)

# Init sequence (HD44780 4-bit)
write4bits(0x03)
time.sleep(0.005)
write4bits(0x03)
time.sleep(0.001)
write4bits(0x03)
time.sleep(0.001)
write4bits(0x02)  # Switch to 4-bit
time.sleep(0.010)

# Now in 4-bit mode
write_cmd(0x28)  # 2 lines, 5x8
time.sleep(0.005)
write_cmd(0x0C)  # Display ON, cursor off
time.sleep(0.005)
write_cmd(0x01)  # Clear
time.sleep(0.005)
write_cmd(0x06)  # Entry mode: inc, no shift
time.sleep(0.005)

# Write test text
write_cmd(0x80)  # Set DDRAM to row 0
time.sleep(0.005)
write_text("Hello Pi!")
write_cmd(0xC0)  # Set DDRAM to row 1 (0x40 + 0x80)
time.sleep(0.005)
write_text("LCD @ 0x38")

print("Text written to LCD.")
print("If you see blocks, turn contrast pot slowly.")
print("If still blocks, try the other direction.")
print("Press any key to exit...")
input()

# Cleanup
write_cmd(0x01)  # Clear
time.sleep(0.005)
write_byte(0x00)
bus.close()
