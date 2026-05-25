import paramiko, os, time

HOST = os.environ.get("SSH_HOST", "192.168.0.8")
USER = os.environ.get("SSH_USER", "root")
PASS = os.environ.get("SSH_PASS", "orangepi")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    return ec, out.strip(), err.strip()

# Create the setup script locally first
setup = r"""#!/bin/bash
set -e
cd /opt/tinyTradeAi

echo "=== Creating venv ==="
python3 -m venv venv
. venv/bin/activate

echo "=== Symlink smbus ==="
ln -sf /usr/lib/python3/dist-packages/smbus.cpython-35m-arm-linux-gnueabihf.so venv/lib/python3.5/site-packages/

echo "=== Installing packages ==="
for pkg in python-dotenv==0.19.2 Flask==1.1.4 requests==2.25.1 schedule==0.6.0 numpy==1.19.5 vaderSentiment==3.3.2 textblob==0.15.3 Pillow==6.2.2; do
    echo "  $pkg ..."
    pip install --no-cache-dir "$pkg" || echo "  FAILED: $pkg"
done

echo "=== Verify ==="
for mod in dotenv flask requests schedule vaderSentiment textblob numpy PIL smbus; do
    python -c "import $mod; print('  $mod OK')" 2>&1 || echo "  $mod FAILED"
done

echo "=== Set LCD address ==="
sed -i 's/LCD_I2C_ADDRESS = 0x00/LCD_I2C_ADDRESS = 0x38/' config.py

echo "=== Unbind rda_sensor ==="
echo 0-003c > /sys/bus/i2c/drivers/rda-sensor/unbind 2>/dev/null
echo "  unbound"

echo "=== Syntax checks ==="
PY=venv/bin/python
for f in lcd/driver.py lcd/display.py lcd/screens.py tests/test_lcd_autodiscover.py tests/test_lcd_hardware.py tests/test_lcd_integration.py; do
    $PY -m py_compile "$f" 2>&1 && echo "  $f OK" || echo "  $f FAIL"
done

echo "=== Tests ==="
for t in tests/test_lcd_autodiscover.py tests/test_lcd_hardware.py tests/test_lcd_integration.py; do
    echo "--- $t ---"
    $PY "$t" 2>&1 || true
done

echo "=== DONE ==="
"""

# Write to local temp file (Unix line endings!)
with open("C:\\Users\\lucky\\AppData\\Local\\Temp\\deploy_on_pi.sh", "wb") as f:
    f.write(setup.replace("\r\n", "\n").encode("utf-8"))

# SCP it over
sftp = client.open_sftp()
sftp.put("C:\\Users\\lucky\\AppData\\Local\\Temp\\deploy_on_pi.sh", "/tmp/deploy_on_pi.sh")
sftp.close()
print("Script uploaded")

# Make executable
run("chmod +x /tmp/deploy_on_pi.sh", 5)

# Run in background
run("nohup bash /tmp/deploy_on_pi.sh > /tmp/deploy.log 2>&1 &", 5)
print("Deploy running in background (PID: ?)")
print("Waiting up to 30 minutes...")

# Poll
for i in range(60):
    time.sleep(30)
    ec, o, e = run("ps aux | grep 'deploy_on_pi.sh' | grep -v grep | wc -l", 5)
    if o.strip() == "0":
        mins = (i+1) * 30 // 60
        secs = (i+1) * 30 % 60
        print("Finished after %dm%ds" % (mins, secs))
        break
    if i % 2 == 0:
        # Show latest progress line
        ec2, o2, e2 = run("tail -3 /tmp/deploy.log", 5)
        print("  [%dm] %s" % ((i+1)*30//60, o2.splitlines()[-1] if o2 else "running..."))

# Show full results
print("\n" + "="*50)
print("DEPLOY LOG:")
print("="*50)
ec, o, e = run("cat /tmp/deploy.log", 30)
print(o)

client.close()
