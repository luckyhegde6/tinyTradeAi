import paramiko

HOST = "192.168.0.8"
USER = "root"
PASS = "orangepi"
TARGET = "/opt/tinyTradeAi"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    lines = out.strip().splitlines() if out.strip() else []
    for line in lines[-15:]:
        print("  %s" % line)
    if err.strip():
        for line in err.strip().splitlines()[-10:]:
            print("  ERR: %s" % line)
    return ec, out, err

# Step 1: Clone
print("=== Step 1: Clone ===")
run("rm -rf %s" % TARGET, 10)
run("git clone --depth 1 --branch feature/lcd-16x2-pcf8574-i2c-integration "
    "https://github.com/luckyhegde6/tinyTradeAi.git %s" % TARGET, 120)

# Step 2: Install smbus via apt
print("\n=== Step 2: Install smbus ===")
run("apt-get update -qq 2>/dev/null", 120)
run("apt-get install -y python3-smbus -qq 2>/dev/null", 60)
run("python3 -c 'import smbus; print(\"smbus OK\")' 2>&1", 5)

# Step 3: Venv
print("\n=== Step 3: Venv ===")
run("cd %s && python3 -m venv venv" % TARGET, 30)

# Step 4: Pip
print("\n=== Step 4: Pip install ===")
run("cd %s && venv/bin/pip install --no-cache-dir -r requirements.txt" % TARGET, 300)

# Step 5: Set LCD address
print("\n=== Step 5: Set LCD address ===")
run("sed -i 's/LCD_I2C_ADDRESS = 0x00/LCD_I2C_ADDRESS = 0x38/' %s/config.py" % TARGET, 5)

# Step 6: Unbind rda_sensor
print("\n=== Step 6: Unbind rda_sensor ===")
run("echo 0-003c > /sys/bus/i2c/drivers/rda-sensor/unbind 2>/dev/null; echo done", 5)

# Step 7: Syntax check
print("\n=== Step 7: Syntax check ===")
for f in ["lcd/driver.py", "lcd/display.py", "lcd/screens.py",
          "tests/test_lcd_autodiscover.py", "tests/test_lcd_hardware.py",
          "tests/test_lcd_integration.py"]:
    ec, _, _ = run("cd %s && venv/bin/python -m py_compile %s 2>&1" % (TARGET, f), 10)
    print("  %s: %s" % (f, "OK" if ec == 0 else "FAIL"))

# Step 8: Autodiscover
print("\n=== Step 8: LCD autodiscover ===")
run("cd %s && venv/bin/python tests/test_lcd_autodiscover.py" % TARGET, 30)

# Step 9: Hardware test
print("\n=== Step 9: LCD hardware test ===")
run("cd %s && venv/bin/python tests/test_lcd_hardware.py" % TARGET, 30)

# Step 10: Integration test
print("\n=== Step 10: LCD integration test ===")
run("cd %s && venv/bin/python tests/test_lcd_integration.py" % TARGET, 30)

client.close()
print("\n=== Complete ===")
