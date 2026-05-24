# Production Deployment & Hardening Guide
## Orange Pi 2G-IOT Edge Terminal

This document provides a production-grade guide to deploying, stabilizing, and hardening **TinyTrade AI** on the ultra-low-memory **Orange Pi 2G-IOT (256MB RAM)**.

---

## 1. Local-to-Edge Code Deployment

Since the board is connected to the same Wi-Fi network, transfer the clean codebase from your developer machine using Secure Copy (SCP).

Open a terminal on your host computer:
```powershell
# In Windows PowerShell, replace <orange-pi-ip> with your board's actual IP
scp -r "F:\Local_git\Study_2026\tinyTradeAi" root@<orange-pi-ip>:/opt/
```

## 2. EOL Debian Stretch Repository Fix (Crucial for Legacy Images)

Since official Debian 9 (Stretch) is **End-of-Life (EOL)**, the package mirrors return `404 Not Found` errors when attempting to run `apt-get install`. You must point your repository source files to the official Debian archives.

Execute these commands **on the Orange Pi**:

```bash
# 1. Back up your current sources list
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

# 2. Overwrite the file to use Debian Archive repositories (trusted bypass is added for expired GPG keys)
sudo tee /etc/apt/sources.list <<EOF
deb [trusted=yes] http://archive.debian.org/debian stretch main contrib non-free
deb [trusted=yes] http://archive.debian.org/debian-security stretch/updates main contrib non-free
EOF

# 3. Update the package list
sudo apt-get update
```

---

## 3. Low-Footprint Environment Setup

SSH into your Orange Pi (`ssh root@<orange-pi-ip>`) and prepare a isolated virtual environment.

```bash
cd /opt/tinyTradeAi

# 1. Initialize virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies with no-cache to conserve critical RAM
pip install --no-cache-dir -r requirements.txt
```

---

## 4. Production Configuration

Create your secure environment file:
```bash
cp .env.example .env
nano .env
```
Fill in your production-grade credentials (Zero Trust Telegram ID, Bot Token).

---

## 5. Production-Grade Hardening (Mandatory for 256MB RAM)

Running Python engines on a 256MB embedded device requires system-level tuning to ensure 100% uptime and prevent random Out-of-Memory (OOM) crashes.

### A. Set Up Swap Space (Crucial Safety Net)
By default, some legacy Armbian/Ubuntu images do not enable virtual swap space. If Python encounters a temporary memory spike, the Linux kernel will instantly kill it. Adding a 512MB swap file creates a vital buffer.

Execute the following commands on the Orange Pi:
```bash
# 1. Create a 512MB swap file
sudo fallocate -l 512M /swapfile
# If fallocate fails, use dd: sudo dd if=/dev/zero of=/swapfile bs=1M count=512

# 2. Set secure permissions
sudo chmod 600 /swapfile

# 3. Format as swap space
sudo mkswap /swapfile

# 4. Activate the swap space
sudo swapon /swapfile

# 5. Make it permanent on boot
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 6. Verify swap is active
free -h
```

### B. Optimize SD Card Wear-and-Tear (Flash Preservation)
Frequent SQLite read/writes and OS logs can wear out cheap MicroSD cards rapidly. Optimize your mount configuration.

Edit `/etc/fstab`:
```bash
sudo nano /etc/fstab
```
Locate your root partition mount entry (`/`) and append the `noatime` option. This stops the kernel from writing file access timestamps every time a file is read:
```text
# Example fstab line modification:
UUID=xxxx-xxxx  /  ext4  defaults,noatime,nodiratime,commit=600  0  1
```
*Note: `commit=600` caches filesystem changes in RAM and flushes them to disk every 10 minutes instead of every 5 seconds, immensely prolonging SD card life.*

### C. Systemd Auto-Recovery Service
Deploy the service using the pre-configured systemd script. This ensures the background daemon restarts automatically if a crash occurs.

```bash
# 1. Install the systemd configuration
sudo cp scripts/tinytrade.service /etc/systemd/system/

# 2. Reload systemd to recognize the new service
sudo systemctl daemon-reload

# 3. Enable the service to launch on boot
sudo systemctl enable tinytrade.service

# 4. Start the service
sudo systemctl start tinytrade.service
```

---

## 6. Operations & Monitoring

### Check Service Status
```bash
sudo systemctl status tinytrade.service
```

### Stream Live System Logs
```bash
journalctl -u tinytrade.service -f -n 100
```

### Inspect SQLite Database Storage
```bash
sqlite3 /opt/tinyTradeAi/database/market.db "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5;"
```

### Restart the Application
```bash
sudo systemctl restart tinytrade.service
```
