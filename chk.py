import paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("192.168.0.11", username="root", password="orangepi", timeout=10)

def r(cmd):
    s = c.exec_command(cmd, timeout=10)
    s[1].channel.recv_exit_status()
    return s[1].read().decode().strip()

print("=== screens.py header ===")
print(r("head -12 /opt/tinyTradeAi/lcd/screens.py"))

print("\n=== LCD import in main ===")
print(r("grep -E 'lcd.screen|render_lcd' /opt/tinyTradeAi/main.py"))

print("\n=== File timestamps ===")
print(r("ls -la /opt/tinyTradeAi/lcd/screens.py /opt/tinyTradeAi/main.py 2>&1"))

print("\n=== main.py running? ===")
print(r("ps aux | grep 'python.*main.py' | grep -v grep | head -3"))

c.close()
