# Python Upgrade Guide (Orange Pi 2G-IOT)

## Why Upgrade?

The Orange Pi runs Debian Stretch (9) with Python 3.5.3. This blocks fixes for 8 Dependabot CVEs because patched package versions require Python 3.6+:

| Package | CVE | Severity | Fix version | Requires |
|---------|-----|----------|-------------|----------|
| Pillow | Buffer overflow | HIGH | 10.x | Python 3.6+ |
| requests | Session verify=False | Moderate | 2.32.x | Python 3.7+ |
| requests | .netrc credential leak | Moderate | 2.32.x | Python 3.7+ |
| requests | Insecure temp file | Moderate | 2.33.x | Python 3.8+ |
| python-dotenv | Symlink in set_key | Moderate | 1.2.2 | Python 3.8+ |
| Pillow | Integer overflow (fonts) | Moderate | 9.x | Python 3.6+ |
| Pillow | PDF infinite loop (DoS) | Moderate | 9.x | Python 3.6+ |
| Flask | Vary: Cookie header | Low | 2.x | Python 3.6+ |

## Option 1: Debian Backports (Python 3.7)

```bash
echo "deb http://deb.debian.org/debian stretch-backports main" >> /etc/apt/sources.list
apt-get update
apt-get install -t stretch-backports python3.7 python3.7-dev python3.7-venv
python3.7 -m venv /opt/tinyTradeAi/venv37
source /opt/tinyTradeAi/venv37/bin/activate
pip install -r /opt/tinyTradeAi/requirements.txt
```

## Option 2: Compile Python 3.8 from Source

```bash
apt-get install -y build-essential libssl-dev zlib1g-dev libncurses5-dev \
  libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev \
  libbz2-dev libexpat1-dev liblzma-dev libffi-dev

wget https://www.python.org/ftp/python/3.8.18/Python-3.8.18.tar.xz
tar xf Python-3.8.18.tar.xz
cd Python-3.8.18
./configure --enable-optimizations
make -j1          # single-core compile takes ~2 hours on 256MB
make altinstall   # installs as python3.8 (doesn't override system python3)
```

## Option 3: Upgrade to Debian 10 (Buster)

Debian 10 (Buster) ships Python 3.7.3 by default.

```bash
# Replace stretch with buster in sources.list
sed -i 's/stretch/buster/g' /etc/apt/sources.list
sed -i 's/stretch/buster/g' /etc/apt/sources.list.d/*.list 2>/dev/null || true

apt-get update
apt-get upgrade -y
apt-get dist-upgrade -y
```

This is a major OS upgrade. It will update the kernel, system libraries, and all packages. The application and systemd service should continue working.

## After Upgrade

1. Create a new venv: `python3.7 -m venv /opt/tinyTradeAi/venv && source /opt/tinyTradeAi/venv/bin/activate`
2. Install deps: `pip install -r requirements.txt`
3. Symlink smbus: `ln -sf /usr/lib/python3/dist-packages/smbus.cpython-35m-arm-linux-gnueabihf.so /opt/tinyTradeAi/venv/lib/python3.7/site-packages/`
4. Update systemd service: `systemctl edit tinytrade.service` → update ExecStart to use new venv Python
5. Restart: `systemctl daemon-reload && systemctl restart tinytrade.service`
