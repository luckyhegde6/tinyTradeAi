# Remote Testing on Orange Pi

## Workflow
Development happens on your local machine. Tests run on the Orange Pi via SSH.

## One-off Test
```bash
ssh root@192.168.0.8 "cd /opt/tinyTradeAi && source venv/bin/activate && python3 tests/test_lcd_hardware.py"
```

## Automated Test Suite
```bash
bash scripts/run_remote_tests.sh              # Run all tests
bash scripts/run_remote_tests.sh test_lcd_hardware.py  # Run specific test
```

## Deploying Code Changes
```bash
# Full deploy
scp -r /path/to/tinyTradeAi root@192.168.0.8:/opt/

# Single file (faster iteration)
scp lcd/driver.py root@192.168.0.8:/opt/tinyTradeAi/lcd/
scp config.py root@192.168.0.8:/opt/tinyTradeAi/
```

## Session Persistence
Always use tmux for long-running operations:
```bash
ssh root@192.168.0.8
tmux new-session -s tinyTrade-test
# Run tests inside tmux — they survive SSH disconnects
```

## Logging
Test logs are written to `/var/log/tinytrade/` on the Orange Pi:
```bash
tail -f /var/log/tinytrade/LCD_Init.log
tail -f /var/log/tinytrade/LCD_Screens.log
```

## Checklist Before Deployment
- [ ] All tests pass on Orange Pi
- [ ] config.py has correct LCD_I2C_ADDRESS
- [ ] rda_sensor blacklisted: `/etc/modprobe.d/rda-sensor-blacklist.conf`
- [ ] Swap file configured (512MB)
- [ ] tmux session ready for main loop
