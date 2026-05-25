# tmux Session Management for Orange Pi

## Why tmux?
SSH connections drop. WiFi disconnects. tmux keeps your session alive even when you get disconnected — just reattach.

## Quick Start
```bash
# Launch pre-configured session
bash scripts/tmux_session.sh

# Attach
tmux attach -t tinyTrade-dev
```

## Manual Commands
```bash
# Create session
tmux new-session -s mywork -d
tmux send-keys -t mywork "cd /opt/tinyTradeAi && source venv/bin/activate" Enter

# Attach/detach
tmux attach -t mywork          # Ctrl+B D to detach

# Windows (tabs)
tmux new-window -t mywork -n logs
tmux send-keys -t mywork:logs "journalctl -u tinytrade -f" Enter
tmux select-window -t mywork:0  # Switch back

# Panes (splits)
# Ctrl+B %  — vertical split
# Ctrl+B "  — horizontal split
# Ctrl+B arrow — navigate panes

# Scroll mode: Ctrl+B [ then PgUp/PgDn, q to quit

# List sessions
tmux list-sessions

# Kill
tmux kill-session -t mywork
```

## Pre-configured Session Layout
The `scripts/tmux_session.sh` script creates 4 windows:
| # | Name | Purpose |
|---|------|---------|
| 0 | main | App/test runner |
| 1 | logs | Log monitoring |
| 2 | i2c | I2C bus monitor |
| 3 | shell | General shell |

## Memory Note
tmux uses ~5MB RAM. On a 256MB device, this is acceptable. Avoid creating more than 2-3 sessions.
