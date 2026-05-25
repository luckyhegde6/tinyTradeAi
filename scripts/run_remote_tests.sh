#!/usr/bin/env bash
# run_remote_tests.sh — Run TinyTrade test suite on Orange Pi via SSH
# Usage: bash scripts/run_remote_tests.sh [test_name]
#   Without arguments, runs all tests.
#   With argument, runs specific test file from tests/

set -e

ORANGE_PI="root@192.168.0.8"
BASE_DIR="/opt/tinyTradeAi"
SSH_CMD="ssh ${ORANGE_PI}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/tmp/tinytrade-remote-test-${TIMESTAMP}.log"
TEST_FILE="${1}"

echo "========================================"
echo " Remote Test Runner"
echo " Host: ${ORANGE_PI}"
echo " Dir:  ${BASE_DIR}"
echo " Log:  ${LOG_FILE}"
echo "========================================"

# Check connectivity
echo ""
echo "--- Checking SSH connectivity ---"
if ! ${SSH_CMD} "hostname" > /dev/null 2>&1; then
    echo "[FAIL] Cannot reach ${ORANGE_PI}"
    echo "  Check: network, SSH service, credentials"
    exit 1
fi
echo "  [PASS] SSH connection OK"

# Check project exists
echo ""
echo "--- Checking project deployment ---"
if ! ${SSH_CMD} "test -d ${BASE_DIR}" > /dev/null 2>&1; then
    echo "[FAIL] Project not found at ${BASE_DIR}"
    echo "  Deploy: scp -r ./tinyTradeAi ${ORANGE_PI}:/opt/"
    exit 1
fi
echo "  [PASS] Project found"

# Activate venv and run
echo ""
echo "--- Running tests ---"
if [ -n "${TEST_FILE}" ]; then
    echo "  Test: ${TEST_FILE}"
    ${SSH_CMD} "cd ${BASE_DIR} && source venv/bin/activate && python3 tests/${TEST_FILE}" 2>&1 | tee "${LOG_FILE}"
else
    echo "  Running full test suite..."

    echo "  [1/3] LCD autodiscover..."
    ${SSH_CMD} "cd ${BASE_DIR} && source venv/bin/activate && python3 tests/test_lcd_autodiscover.py" 2>&1 | tee -a "${LOG_FILE}"

    echo ""
    echo "  [2/3] LCD hardware..."
    ${SSH_CMD} "cd ${BASE_DIR} && source venv/bin/activate && python3 tests/test_lcd_hardware.py" 2>&1 | tee -a "${LOG_FILE}"

    echo ""
    echo "  [3/3] LCD integration..."
    ${SSH_CMD} "cd ${BASE_DIR} && source venv/bin/activate && python3 tests/test_lcd_integration.py" 2>&1 | tee -a "${LOG_FILE}"
fi

echo ""
echo "========================================"
echo " Test run complete — log saved to ${LOG_FILE}"
echo "========================================"
