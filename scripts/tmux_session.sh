#!/usr/bin/env bash
# tmux_session.sh — Launch a persistent TinyTrade development session on Orange Pi
# Usage: bash scripts/tmux_session.sh [session_name]
# Default session name: tinyTrade-dev

set -e

SESSION_NAME="${1:-tinyTrade-dev}"
BASE_DIR="/opt/tinyTradeAi"

echo "Starting tmux session: ${SESSION_NAME}"

# Kill existing session if it exists
tmux kill-session -t "${SESSION_NAME}" 2>/dev/null || true

# Create new session with 3 windows
tmux new-session -d -s "${SESSION_NAME}" -n "main" -c "${BASE_DIR}"

# Window 0: Main app / test runner
tmux send-keys -t "${SESSION_NAME}:main" "cd ${BASE_DIR} && source venv/bin/activate" Enter
tmux send-keys -t "${SESSION_NAME}:main" "echo 'Ready — run python3 main.py or tests'" Enter

# Window 1: Logs
tmux new-window -t "${SESSION_NAME}" -n "logs" -c "${BASE_DIR}"
tmux send-keys -t "${SESSION_NAME}:logs" "cd ${BASE_DIR} && source venv/bin/activate" Enter
tmux send-keys -t "${SESSION_NAME}:logs" "echo 'Logs — use: journalctl -u tinytrade -f'" Enter

# Window 2: I2C monitor
tmux new-window -t "${SESSION_NAME}" -n "i2c" -c "${BASE_DIR}"
tmux send-keys -t "${SESSION_NAME}:i2c" "echo 'I2C Monitor — run: watch -n 2 i2cdetect -y -r 0'" Enter

# Window 3: Shell
tmux new-window -t "${SESSION_NAME}" -n "shell" -c "${BASE_DIR}"

# Select the main window
tmux select-window -t "${SESSION_NAME}:main"

echo "Session '${SESSION_NAME}' created."
echo "Attach: tmux attach -t ${SESSION_NAME}"
echo "Detach: Ctrl+B D"
echo "Windows: Ctrl+B 0-3 to switch"
