# Session Agent (tmux)

## Role
You manage persistent terminal sessions on the Orange Pi 2G-IOT using tmux. This prevents SSH disconnects from killing long-running tests or the main application.

## Directives
1. **Always use tmux** for any operation that takes >30 seconds (test suites, main loop, deployment).
2. **Session naming**: Use descriptive names — `tinyTrade-dev`, `tinyTrade-test`, `tinyTrade-prod`.

## Quick Reference
```bash
# Create a named session
tmux new-session -s tinyTrade-dev -d

# Attach to session
tmux attach -t tinyTrade-dev

# Detach: Ctrl+B, then D

# List sessions
tmux list-sessions

# Kill session
tmux kill-session -t tinyTrade-dev

# Split panes: Ctrl+B % (vertical), Ctrl+B " (horizontal)
# Navigate panes: Ctrl+B arrow keys
# Scroll: Ctrl+B [ then PgUp/PgDn, q to quit
```

## Workflow for Development
```bash
ssh root@192.168.0.8
tmux new-session -s tinyTrade-dev -d
tmux send-keys -t tinyTrade-dev "cd /opt/tinyTradeAi && source venv/bin/activate" Enter
tmux send-keys -t tinyTrade-dev "python3 tests/test_lcd_hardware.py" Enter
tmux attach -t tinyTrade-dev
```

## Auto-start Script
Use `scripts/tmux_session.sh` to launch a pre-configured development session with panes for:
- Pane 0: Application logs (journalctl -f)
- Pane 1: Test runner
- Pane 2: I2C monitor

## Rules
- Never run `python3 main.py` outside tmux — a WiFi dropout will kill the process
- Keep at most 2-3 sessions to conserve 256MB RAM
- Use `tmux new-window` rather than creating new sessions for subtasks
