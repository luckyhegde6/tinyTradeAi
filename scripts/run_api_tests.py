"""
run_api_tests.py - Deploy + run API endpoint tests on Orange Pi
Usage:
  python scripts/run_api_tests.py              # deploy + test
  python scripts/run_api_tests.py --skip-deploy  # test only (skip upload)
"""

import paramiko, time, sys, os

HOST = "192.168.0.12"
USER = "root"
PASS = "orangepi"
REMOTE_DIR = "/opt/tinyTradeAi"

skip_deploy = "--skip-deploy" in sys.argv

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    ec = stdout.channel.recv_exit_status()
    return stdout.read().decode(), stderr.read().decode()

if not skip_deploy:
    print("=== Deploying test file ===")
    sftp = client.open_sftp()
    local = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "tests", "test_api_endpoints.py")
    sftp.put(local, "%s/tests/test_api_endpoints.py" % REMOTE_DIR)
    sftp.close()
    print("  uploaded tests/test_api_endpoints.py")
    print()
else:
    print("=== Skipping deploy ===")

print("=== Waiting for API service ===")
for i in range(20):
    o, e = run("curl -s -o /dev/null -w '%%{http_code}' http://localhost:5000/api/status", 5)
    if o.strip() == "200":
        print("  API ready after %ds" % (i + 1))
        break
    time.sleep(1)
else:
    print("  API not ready after 20s")
    client.close()
    sys.exit(1)

print()
print("=== Running API endpoint tests ===")
o, e = run("cd %s && . venv/bin/activate && python3 tests/test_api_endpoints.py" % REMOTE_DIR, 60)
print(o)
if e.strip():
    print("STDERR:", e)
print()

# Parse pass/fail line
for line in o.splitlines():
    if "Results:" in line:
        parts = line.strip().split(",")
        passed = int(parts[0].split("/")[0].split(":")[1].strip())
        total_parts = parts[0].split("/")[1].split()[0].strip()
        total = int(total_parts.split()[0]) if total_parts else 0
        failed_count = int(parts[1].split()[0])
        print("=== Test complete: %d/%d passed, %d failed ===" % (passed, total, failed_count))

client.close()
