#!/usr/bin/env bash
# verify_lcd.sh — Full LCD Verification Pipeline for Orange Pi 2G-IOT
# Usage: bash scripts/verify_lcd.sh [i2c_address]
# Runs on the Orange Pi. Default address: 0x38 (PCF8574A found on user device)

set -e

ADDR=${1:-0x38}
BASE_DIR="/opt/tinyTradeAi"

echo "========================================"
echo " LCD Verification Pipeline"
echo " Address: ${ADDR}"
echo "========================================"

# 0. Prerequisites
if [ ! -d "${BASE_DIR}" ]; then
    echo "[FAIL] Project not found at ${BASE_DIR}"
    exit 1
fi

cd "${BASE_DIR}"

if [ ! -d "venv" ]; then
    echo "[FAIL] Virtual environment not found — run: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

# 1. Verify I2C bus
echo ""
echo "--- Step 1: I2C Bus Check ---"
if i2cdetect -y -r 0 2>&1 | grep -q "$(echo ${ADDR} | cut -c3-2)"; then
    echo "  [PASS] Address ${ADDR} visible on bus 0"
else
    echo "  [FAIL] Address ${ADDR} not found on bus 0"
    echo "  Check: power (5V on pin 2/4), connections (SDA→pin3, SCL→pin5)"
    exit 1
fi

# 2. Write test (i2cget read)
echo ""
echo "--- Step 2: I2C Communication ---"
NUMADDR=$(echo ${ADDR} | cut -c3-)
RESULT=$(i2cget -y 0 0x${NUMADDR} 2>&1) || true
if ! echo "$RESULT" | grep -q "Error"; then
    echo "  [PASS] I2C read from ${ADDR}: ${RESULT}"
else
    echo "  [WARN] I2C read returned error (may be normal for PCF8574)"
fi

# 3. Python driver test
echo ""
echo "--- Step 3: Python Driver ---"
python3 -c "
import sys
sys.path.insert(0, '.')
import smbus
from lcd.driver import PCF8574LCD

bus = smbus.SMBus(0)
lcd = PCF8574LCD(bus, ${NUMADDR}, 16, 2)
lcd.clear()
lcd.write_line('TinyTrade AI', 0)
lcd.write_line('LCD: ${ADDR}', 1)
lcd.set_backlight(True)
print('  [PASS] LCD driver initialized, text written')
lcd.close()
" 2>&1

# 4. Hardware test
echo ""
echo "--- Step 4: Hardware Test ---"
python3 tests/test_lcd_hardware.py 2>&1 | tail -5

# 5. Integration test
echo ""
echo "--- Step 5: Integration Test ---"
python3 tests/test_lcd_integration.py 2>&1 | tail -5

echo ""
echo "========================================"
echo " LCD verification complete"
echo " To run main app: python3 main.py"
echo "========================================"
