#!/usr/bin/env bash
# startup.sh - TinyTrade startup: unbind rda_sensor, verify display, launch app
# Usage:
#   bash scripts/startup.sh          (runs in foreground - for systemd)
#   bash scripts/startup.sh --tmux   (launches in tmux - for manual/SSH)
# Deployed at: /opt/tinyTradeAi/scripts/startup.sh

BASE_DIR="/opt/tinyTradeAi"
LOG_FILE="/var/log/tinytrade/startup.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== TinyTrade Startup Check ==="

# 1. Wait for /dev/i2c-0 to be ready (retry up to 10s)
for i in $(seq 1 10); do
    if [ -e /dev/i2c-0 ]; then
        log "/dev/i2c-0 ready after ${i}s"
        break
    fi
    if [ "$i" -eq 10 ]; then
        log "/dev/i2c-0 MISSING after 10s - continuing anyway"
    fi
    sleep 1
done

# 2. Unbind rda_sensor from 0x3C (frees OLED I2C address)
if [ -e /sys/bus/i2c/drivers/rda-sensor/0-003c ]; then
    echo 0-003c > /sys/bus/i2c/drivers/rda-sensor/unbind 2>/dev/null
    log "rda_sensor unbound from 0x3C"
    sleep 1  # let I2C bus settle
else
    log "rda_sensor not at 0x3C (already free or absent)"
fi

# 3. Verify I2C bus
if [ -e /dev/i2c-0 ]; then
    log "/dev/i2c-0 present [OK]"
else
    log "/dev/i2c-0 MISSING [FAIL]"
fi

# 4. Probe OLED at 0x3C (retry with backoff)
if command -v i2cget &>/dev/null; then
    for i in 1 2 3; do
        if i2cget -y 0 0x3c &>/dev/null; then
            log "OLED at 0x3C: ACK on attempt $i [OK]"
            break
        fi
        if [ "$i" -eq 3 ]; then
            log "OLED at 0x3C: no ACK after 3 attempts [WARN - will retry in-app]"
        else
            sleep $((i * 2))
        fi
    done
fi

# 5. Probe LCD at 0x38 (non-critical)
if command -v i2cget &>/dev/null; then
    i2cget -y 0 0x38 &>/dev/null && \
        log "LCD at 0x38: ACK [OK]" || \
        log "LCD at 0x38: no ACK (non-critical)"
fi

log "=== Launching TinyTrade ==="

if [ "$1" = "--tmux" ]; then
    tmux kill-session -t tinyTrade-prod 2>/dev/null || true
    tmux new-session -d -s tinyTrade-prod -c "$BASE_DIR"
    tmux send-keys -t tinyTrade-prod "cd $BASE_DIR && . venv/bin/activate && python main.py" Enter
    log "Launched in tmux session 'tinyTrade-prod'"
    sleep 2
    pgrep -f "python main.py" &>/dev/null && \
        log "main.py running [OK]" || \
        log "main.py NOT running [FAIL]"
else
    cd "$BASE_DIR"
    . venv/bin/activate
    log "Starting main.py (foreground)..."
    exec python main.py
fi
