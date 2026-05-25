import smbus, time, sys

bus = smbus.SMBus(0)
ADDR = 0x38
BL = 0x08
E = 0x04
RS = 0x01

def w(v):
    bus.write_byte(ADDR, v)
    time.sleep(0.0001)

def strobe(data):
    w(data | E | BL)
    time.sleep(0.002)
    w(data & ~E | BL)
    time.sleep(0.002)

def nib(n, rs=0):
    strobe(((n << 4) & 0xF0) | rs)

def send(b, rs=0):
    strobe((b & 0xF0) | rs)
    time.sleep(0.0005)
    strobe(((b << 4) & 0xF0) | rs)

def cmd(c):
    send(c, 0)

def txt(s):
    for ch in s:
        send(ord(ch), RS)

print("Starting...")

w(BL)
time.sleep(0.10)

for _ in range(3):
    nib(0x03)
    time.sleep(0.005)
nib(0x02)
time.sleep(0.010)

cmd(0x28); time.sleep(0.005)
cmd(0x0C); time.sleep(0.005)
cmd(0x01); time.sleep(0.010)
cmd(0x06); time.sleep(0.005)

cmd(0x80); time.sleep(0.002)
txt("Hello from Pi!")

cmd(0xC0); time.sleep(0.002)
txt("LCD @0x38 WORKS!")

print("Written! Adjust contrast slowly.")
sys.stdout.flush()
raw_input("Press Enter to exit...")

cmd(0x01)
time.sleep(0.005)
w(0)
bus.close()
