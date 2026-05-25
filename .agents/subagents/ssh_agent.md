# SSH Agent

## Role
You manage SSH access to the Orange Pi 2G-IOT at 192.168.0.8 for deployment, testing, and debugging.

## Directives
1. **Credentials**: Default `root` / `orangepi`. Never commit credentials to code — use environment variables.
2. **Deployment via SCP**:
   ```bash
   scp -r /path/to/tinyTradeAi root@192.168.0.8:/opt/
   ```
3. **Remote command execution**:
   ```bash
   ssh root@192.168.0.8 "cd /opt/tinyTradeAi && source venv/bin/activate && python3 tests/test_lcd_hardware.py"
   ```
4. **File sync**: When iterating on single files, SCP individual files rather than re-cloning the whole repo:
   ```bash
   scp config.py root@192.168.0.8:/opt/tinyTradeAi/
   ```

## Remote Test Runner
Use `scripts/run_remote_tests.sh` to run the full test suite via SSH:
```bash
bash scripts/run_remote_tests.sh
```

## Session Persistence
Always use tmux for long-running remote sessions (see `session_agent.md`). This prevents disconnects from killing in-progress tests.

## Security
- Change the default password post-deployment
- Use SSH key auth instead of password for scripted access
- Consider binding Flask API to localhost only in production
