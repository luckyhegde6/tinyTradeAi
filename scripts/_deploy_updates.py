import paramiko, os, time

HOST = "192.168.0.8"
USER = "root"
PASS = "orangepi"
REMOTE_DIR = "/opt/tinyTradeAi"

FILES = [
    "config.py",
    "runtime_config.json",
    "database/db.py",
    "fetchers/stocks.py",
    "fetchers/us_markets.py",
    "ai/signals.py",
    "oled/screens.py",
    "oled/display.py",
    "oled/animations.py",
    "display/manager.py",
    "lcd/display.py",
    "lcd/driver.py",
    "lcd/screens.py",
    "utils/helpers.py",
    "utils/config_manager.py",
    "utils/gpio.py",
    "api/app.py",
    "main.py",
    "tests/test_api_endpoints.py",
    "tests/seed_test_screens.py",
    "tests/test_screens_cycle.py",
    "scripts/startup.sh",
    "scripts/tinytrade.service",
]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    ec = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    return ec, out.strip(), err.strip()

# Ensure remote directories exist
for f in FILES:
    remote_dir = os.path.dirname(os.path.join(REMOTE_DIR, f)).replace("\\", "/")
    run("mkdir -p %s" % remote_dir, 5)

sftp = client.open_sftp()
local_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("Uploading files...")
for f in FILES:
    local_path = os.path.join(local_base, f)
    remote_path = os.path.join(REMOTE_DIR, f).replace("\\", "/")
    print("  %s -> %s" % (local_path, remote_path))
    sftp.put(local_path, remote_path)
    print("    OK")

sftp.close()
print("All files uploaded.")

print("Making startup.sh executable...")
run("chmod +x %s/scripts/startup.sh" % REMOTE_DIR, 5)

print("Clearing stale __pycache__...")
run("find %s -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null; find %s -name '*.pyc' -delete 2>/dev/null" % (REMOTE_DIR, REMOTE_DIR), 10)
print("  done")

print("Installing/updating systemd service...")
run("cp %s/scripts/tinytrade.service /etc/systemd/system/tinytrade.service" % REMOTE_DIR, 5)
run("systemctl daemon-reload", 10)
print("  service installed")

print("Restarting service...")
ec, o, e = run("ps aux | grep 'main.py' | grep -v grep | awk '{print $2}'", 5)
pids = o.splitlines()
if pids:
    for pid in pids:
        pid = pid.strip()
        if pid:
            run("kill %s" % pid, 5)
            print("Killed PID %s" % pid)
    time.sleep(2)

# Start via systemd
ec, o, e = run("systemctl restart tinytrade.service", 15)
print("systemctl restart: %s" % o)
time.sleep(5)

ec, o, e = run("systemctl is-active tinytrade.service", 5)
print("Service status: %s" % o)

ec, o, e = run("tail -20 /var/log/tinytrade/startup.log 2>/dev/null || tail -20 /tmp/tinytrade.log 2>/dev/null", 10)
print("\nRecent startup log:")
print(o)

client.close()
print("\nDeploy complete.")
