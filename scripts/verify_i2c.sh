#!/usr/bin/env bash
# verify_i2c.sh — I2C Bus Health Check for Orange Pi 2G-IOT
# Usage: bash scripts/verify_i2c.sh [bus_number]
# Runs on the Orange Pi directly.

set -e

BUS=${1:-0}
PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL+1)); echo "  [FAIL] $1"; }

echo "========================================"
echo " I2C Bus Health Check — Bus ${BUS}"
echo "========================================"

# 1. Check device file exists
if [ -e "/dev/i2c-${BUS}" ]; then
    pass "/dev/i2c-${BUS} exists"
else
    fail "/dev/i2c-${BUS} not found — enable I2C in orangepi-config"
fi

# 2. Check i2cdetect works
OUTPUT=$(i2cdetect -y -r "${BUS}" 2>&1) || true
if echo "$OUTPUT" | grep -q "Error"; then
    fail "i2cdetect failed on bus ${BUS}"
else
    pass "i2cdetect scan completed"
fi

# 3. Check for kernel address conflicts (UU)
UU_COUNT=$(echo "$OUTPUT" | grep -o 'UU' | wc -l)
echo "  Kernel-claimed addresses: ${UU_COUNT} (onboard peripherals — OK)"

# 4. Check for known LCD addresses
for ADDR in 27 3f 38 39 3e; do
    RESULT=$(i2cget -y "${BUS}" 0x"${ADDR}" 2>&1) || true
    if ! echo "$RESULT" | grep -q "Error"; then
        pass "LCD detected at 0x${ADDR}"
    fi
done

# 5. Check for OLED (handle rda_sensor conflict)
OLED=$(i2cget -y "${BUS}" 0x3c 2>&1) || true
if echo "$OLED" | grep -q "Error"; then
    echo "  [INFO] OLED at 0x3C not responding — may be claimed by rda_sensor driver"
    echo "         Run: echo 0-003c > /sys/bus/i2c/drivers/rda-sensor/unbind"
fi

echo "----------------------------------------"
echo " Results: ${PASS} passed, ${FAIL} failed"
echo "========================================"
exit ${FAIL}
