import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("192.168.0.11", username="root", password="orangepi", timeout=10)

def run(cmd, timeout=15):
    s = c.exec_command(cmd, timeout=timeout)
    ec = s[1].channel.recv_exit_status()
    return ec, s[1].read().decode("utf-8", errors="replace"), s[2].read().decode("utf-8", errors="replace")

# Check I2C bus speed
print("=== I2C bus speed ===")
ec, o, e = run("cat /sys/kernel/debug/clk/i2c0_clk/clk_rate 2>/dev/null || cat /sys/class/i2c-adapter/i2c-0/of_node/clock-frequency 2>/dev/null || echo 'N/A'", 5)
print("clock:", o)

print("\n=== I2C bus details ===")
ec, o, e = run("i2cdetect -l 2>&1; echo ---; i2cget -y 0 0x38 2>&1", 10)
print(o)

print("\n=== Quick i2cset test (toggle backlight) ===")
# Turn backlight OFF
ec, o, e = run("i2cset -y 0 0x38 0x00; sleep 1; i2cset -y 0 0x38 0x08", 5)
print("Toggled backlight. Did it blink?")

print("\n=== Write minimal init via i2cset ===")
# Use a shell script for the full init sequence
script = """#!/bin/bash
# PCF8574 LCD init via i2cset
# Pin mapping: RS=P0, RW=P1, E=P2, BL=P3, D4=P4, D5=P5, D6=P6, D7=P7

ADDR=0x38
WR() { i2cset -y 0 $ADDR $1; }
SLEEP() { sleep $1; }

# Power-up: BL on, everything else low
WR 0x08
SLEEP 0.05

# Init sequence in 8-bit mode (send nibble 0x03 = 0011 on D4-D7)
# 0x03 nibble: P4=1, P5=1 => 0x30 to PCF8574
# E high: 0x30 | 0x04 | 0x08 = 0x3C
# E low:  0x30 | 0x00 | 0x08 = 0x38
for i in 1 2 3; do
  WR 0x3C; SLEEP 0.005
  WR 0x38; SLEEP 0.005
done

# Switch to 4-bit mode: nibble 0x02 = 0010 on D4-D7
# 0x02 nibble: P4=0, P5=1 => 0x20
# E high: 0x20 | 0x04 | 0x08 = 0x2C
# E low:  0x20 | 0x00 | 0x08 = 0x28
WR 0x2C; SLEEP 0.005
WR 0x28; SLEEP 0.010

# Now in 4-bit mode. FunctionSet 0x28 = 2-line, 5x8
fn_high=0x2C; fn_low=0x0C
WR $fn_high; SLEEP 0.002
WR 0x28; SLEEP 0.002
WR $fn_low; SLEEP 0.002
WR 0x08; SLEEP 0.002

# Display ON 0x0C
WR 0x0C; SLEEP 0.002
WR 0x08; SLEEP 0.002
WR 0xCC; SLEEP 0.002
WR 0xC8; SLEEP 0.002

# Clear 0x01
WR 0x0C; SLEEP 0.002
WR 0x08; SLEEP 0.002
WR 0x1C; SLEEP 0.002
WR 0x18; SLEEP 0.005

# Entry mode 0x06
WR 0x0C; SLEEP 0.002
WR 0x08; SLEEP 0.002
WR 0xCC; SLEEP 0.002
WR 0xC8; SLEEP 0.002

# Set DDRAM to row 0: 0x80
WR 0x8C; SLEEP 0.002
WR 0x88; SLEEP 0.002
WR 0x0C; SLEEP 0.002
WR 0x08; SLEEP 0.002

# Write 'H' (0x48) with RS=1
# RS=1 => OR with 0x01
# High nibble 0x04: P7=0,P6=1,P5=0,P4=0 => 0x40 | RS=0x41
WR 0x4D; SLEEP 0.002
WR 0x49; SLEEP 0.002
# Low nibble 0x08: P7=1,P6=0,P5=0,P4=0 => 0x80 | RS=0x81
WR 0x8D; SLEEP 0.002
WR 0x89; SLEEP 0.002

echo "DONE"
"""

# Write script to remote
with c.open_sftp().file("/tmp/i2cset_init.sh", "w") as f:
    f.write(script)

ec, o, e = run("chmod +x /tmp/i2cset_init.sh", 5)
ec, o, e = run("bash /tmp/i2cset_init.sh 2>&1", 30)
print(o)
if e: print("ERR:", e[:200])

c.close()
