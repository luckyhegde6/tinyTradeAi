import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("192.168.0.8", username="root", password="orangepi", timeout=10)

def r(cmd, t=10):
    s = c.exec_command(cmd, timeout=t)
    s[1].channel.recv_exit_status()
    return s[1].read().decode().strip() + " | " + s[2].read().decode().strip()

print("=== i2cdetect -y 0 ===")
print(r("i2cdetect -y 0"))

print("\n=== i2cdetect -y 0 -r ===")
print(r("i2cdetect -y 0 -r"))

print("\n=== Unbind rda_sensor at all addresses ===")
for a in ["10", "13", "14", "15", "16", "3c"]:
    ec, o, e = r("echo 0-00%s > /sys/bus/i2c/drivers/rda-sensor/unbind 2>&1; echo ok" % a)
    print("  0-%s: %s" % (a, o))

print("\n=== i2cdetect after unbind ===")
print(r("i2cdetect -y 0"))

print("\n=== Try i2cget at 0x3C and 0x38 ===")
print("  0x3C:", r("i2cget -y 0 0x3C 2>&1"))
print("  0x38:", r("i2cget -y 0 0x38 2>&1"))
print("  0x27:", r("i2cget -y 0 0x27 2>&1"))
print("  0x3F:", r("i2cget -y 0 0x3F 2>&1"))

print("\n=== I2C bus info ===")
print(r("i2cdetect -l 2>&1"))

c.close()
