import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("192.168.0.11", username="root", password="orangepi", timeout=10)

def run(cmd, timeout=15):
    s = c.exec_command(cmd, timeout=timeout)
    ec = s[1].channel.recv_exit_status()
    return ec, s[1].read().decode("utf-8", errors="replace"), s[2].read().decode("utf-8", errors="replace")

ec, o, e = run('cd /opt/tinyTradeAi && echo "" | timeout 10 venv/bin/python /tmp/raw_lcd_test.py 2>&1', 15)
print("=== Raw LCD test ===")
print(o)
if e: print("STDERR:", e[:300])
print("EXIT:", ec)

print("\n=== I2C bus scan ===")
ec, o, e = run("i2cdetect -y 0 2>&1", 10)
print(o)

print("\n=== LCD address in config ===")
ec, o, e = run("grep LCD_I2C_ADDRESS /opt/tinyTradeAi/config.py", 5)
print(o)

c.close()
