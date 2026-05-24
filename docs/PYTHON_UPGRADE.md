# Python Upgrade Guide (3.5.3 → 3.7+)

## Context
Orange Pi 2G-IOT ships with Python 3.5.3 (EOL). Many modern packages like `luma.oled` require Python 3.6+. Debian repos on this device don't have newer Python versions, so compilation from source is necessary.

## Prerequisites
- Build tools and dependencies installed
- ~500MB free space in `/tmp` for compilation
- 20-30 minutes for compilation (single-job due to 256MB RAM constraint)

## Step 1: Install Build Dependencies

```bash
sudo apt-get update
sudo apt-get install -y build-essential zlib1g-dev libssl-dev libffi-dev wget
```

## Step 2: Download Python 3.7.9

```bash
cd /tmp
wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz
tar xzf Python-3.7.9.tgz
cd Python-3.7.9
```

**Troubleshooting Download:**
- If 404 error occurs, check available versions at https://www.python.org/ftp/python/
- Python 3.7.9 is widely available and stable
- Avoid 3.7.18 if it fails to download

## Step 3: Configure for Embedded Device

```bash
./configure --prefix=/usr/local
```

This installs to `/usr/local` (standard location that doesn't conflict with system Python).

## Step 4: Compile (Single-Job Mode)

```bash
# CRITICAL: Use -j1 (single job) to prevent OOM kill on 256MB RAM
make -j1
```

**What to watch for:**
- Compilation takes 20-30 minutes
- Monitor for "virtual memory exhausted" or OOM messages
- If it stalls, the device may be out of memory; restart and retry

## Step 5: Install

```bash
sudo make install
```

## Step 6: Verify Installation

```bash
python3.7 --version
pip3.7 --version
```

Expected output:
```
Python 3.7.9
pip 19.x.x from ...
```

## Step 7: Set Up Virtual Environment

```bash
cd /opt/tinyTradeAi  # or your project root
python3.7 -m venv venv
source venv/bin/activate
# Prompt should now show (venv) prefix
```

## Step 8: Install Project Dependencies

```bash
pip install --no-cache-dir -r requirements.txt
```

The `--no-cache-dir` flag conserves RAM and SD card write cycles.

## Step 9: Cleanup (Optional but Recommended)

Remove compilation artifacts to free ~500MB:

```bash
sudo rm -rf /tmp/Python-3.7.9 /tmp/Python-3.7.9.tgz
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Objects/typeobject.o: Error 1` (OOM) | **See "Out of Memory Error" section below** |
| 404 downloading Python | Check https://www.python.org/ftp/python/ for available versions |
| Compilation hangs/stalls | Device likely OOM; restart and retry with memory optimizations |
| `command not found: python3.7` | Check `/usr/local/bin/python3.7` exists; may need to rehash shell |
| pip fails with SSL errors | Rebuild Python with libssl-dev installed (rerun step 1) |

## Out of Memory Error During Compilation

The 256MB RAM constraint is severe. If you see `Objects/typeobject.o: Error 1` or similar errors, the compiler ran out of memory.

### Solution: Minimize Memory Usage

**Option 1: Clean and Retry with Memory Optimization** (Fastest)

```bash
# Stop any background processes
killall -9 node python npm 2>/dev/null || true

# Clear caches
sync && echo 3 > /proc/sys/vm/drop_caches

# Go back to build directory
cd /tmp/Python-3.7.9

# Clean previous build
make distclean 2>/dev/null || true

# Configure with minimal features
./configure --prefix=/usr/local \
    --disable-optimizations \
    --disable-ipv6 \
    --without-cxx-main \
    --with-system-expat \
    --disable-test-modules

# Compile with aggressive memory limiting
CFLAGS="-O0" make -j1

# If still OOM, try even more aggressive:
# CFLAGS="-O0 -fno-inline" make -j1

# Install
sudo make install
```

**Option 2: Enable Swap** (More Reliable but Slower)

```bash
# Create swap file (1GB, takes ~2 min)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Verify
free -h

# Now retry compilation
cd /tmp/Python-3.7.9
make distclean
./configure --prefix=/usr/local
make -j1
sudo make install

# Remove swap after (to save SD card writes)
sudo swapoff /swapfile
sudo rm /swapfile
```

**Option 3: Use Pre-built Python** (Easiest)

Check if your Debian repo has Python 3.8 or 3.9 available:

```bash
apt-cache search python3.8 python3.9
```

If available, may be faster than compiling.

### Verification After Fix

```bash
python3.7 --version
pip3.7 --version
```

If still failing, proceed to Option 4.

**Option 4: Lightweight Python (PicoTon)**

As last resort, use minimal Python fork designed for embedded systems:

```bash
# Check if available
apt-cache search python3-minimal
apt-get install python3-minimal
```

Then use `pip` to install only required packages.

## Integration with luma.oled

Once Python 3.7 is installed and venv activated, install the OLED library:

```bash
pip install --no-cache-dir luma.oled
```

Then test the display:

```bash
python3 - <<'EOF'
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

serial = i2c(port=0, address=0x3C)
device = ssd1306(serial)
with canvas(device) as draw:
    draw.text((0, 0), "Hello OLED!", fill="white")
print("Display OK!")
EOF
```

## Related Documentation
- [ORANGE_PI_SETUP.md](ORANGE_PI_SETUP.md) - Initial device setup
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Deployment instructions
- [oled/README.md](../oled/README.md) - OLED driver integration
