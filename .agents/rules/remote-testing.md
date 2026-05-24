# Rule: Remote Testing Protocol

## When to Use Remote Testing
- Any hardware test that requires the Orange Pi's I2C bus
- Integration tests that involve OLED/LCD displays
- Long-running main loop tests (always via tmux)

## Test Sequence
1. **Local commit**: Ensure all changes are committed on the dev machine
2. **SCP deploy**: Copy individual changed files to the Orange Pi
3. **SSH execute**: Run tests via `bash scripts/run_remote_tests.sh`
4. **Log inspection**: Check logs at `/var/log/tinytrade/` on the Orange Pi
5. **Fix loop**: If tests fail, fix locally, SCP the changed file, re-run

## SSH Credentials
- Default: `root` / `orangepi`
- After first deployment, set up SSH key auth:
  ```bash
  ssh-copy-id root@192.168.0.8
  ```
- NEVER commit credentials to the repository

## Session Management
- Tests under 10 seconds: run directly via SSH
- Tests over 10 seconds or main loop: use tmux
- Use `scripts/tmux_session.sh` to create a pre-configured session

## Logging Convention
- All loggers write to stdout AND `/var/log/tinytrade/<name>.log`
- Log level: INFO for normal operation, DEBUG for troubleshooting
- Log format: `[timestamp] [name] [level] message`
