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
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    lines = out.strip().splitlines() if out.strip() else []
    for line in lines[-15:]:
        print("  %s" % line)
    if err.strip():
        for line in err.strip().splitlines()[-10:]:
            print("  ERR: %s" % line)
    return exit_code, out, err

# Step 1: Re-clone (to get latest commit with Python 3.5 fixes)
print("=== Step 1: Clone repo ===")
run("rm -rf %s" % TARGET, 10)
run("git clone --depth 1 --branch feature/lcd-16x2-pcf8574-i2c-integration https://github.com/luckyhegde6/tinyTradeAi.git %s" % TARGET, timeout=120)

# Step 2: Install system packages
print("\n=== Step 2: Install system packages ===")
run("apt-get install -y python3-smbus -qq 2>/dev/null", timeout=60)

# Step 3: Create venv
print("\n=== Step 3: Create venv ===")
run("cd %s && python3 -m venv venv" % TARGET, 30)

# Step 4: Install pip deps
print("\n=== Step 4: Install pip deps ===")
run("cd %s && venv/bin/pip install --no-cache-dir -r requirements.txt" % TARGET, timeout=300)

# Step 5: Set LCD address
print("\n=== Step 5: Set LCD address ===")
run("sed -i 's/LCD_I2C_ADDRESS = 0x00/LCD_I2C_ADDRESS = 0x38/' %s/config.py" % TARGET, 5)
run("grep LCD_I2C_ADDRESS %s/config.py" % TARGET, 5)

# Step 6: Unbind rda_sensor
print("\n=== Step 6: Unbind rda_sensor ===")
run("echo 0-003c > /sys/bus/i2c/drivers/rda-sensor/unbind 2>/dev/null; echo done", 5)

# Step 6: Test syntax only (Python 3.5 check)
print("\n=== Step 6: Syntax check ===")
for f in ["lcd/driver.py", "lcd/display.py", "lcd/screens.py"]:
    run("cd %s && venv/bin/python -m py_compile %s 2>&1" % (TARGET, f), 10)

# Step 7: Run autodiscover
print("\n=== Step 7: LCD autodiscover ===")
run("cd %s && venv/bin/python tests/test_lcd_autodiscover.py" % TARGET, 30)

# Step 8: Hardware test
print("\n=== Step 8: LCD hardware test ===")
run("cd %s && venv/bin/python tests/test_lcd_hardware.py" % TARGET, 30)

# Step 9: Integration test
print("\n=== Step 9: LCD integration test ===")
run("cd %s && venv/bin/python tests/test_lcd_integration.py" % TARGET, 30)

client.close()
print("\n=== Complete ===")
