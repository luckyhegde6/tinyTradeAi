# Test Agent

## Role
You ensure all hardware and software tests pass before deployment. You maintain the test pipeline and verify integration between modules.

## Directives
1. **Test tiers** (run in order):
   - **Tier 1 (Unit)**: Python syntax check, import verification
   - **Tier 2 (Hardware)**: I2C detection, LCD/OLED init
   - **Tier 3 (Integration)**: Singleton patterns, config loading, data rendering

2. **LCD test pipeline** (on Orange Pi):
   ```bash
   # Tier 2
   python3 tests/test_lcd_autodiscover.py
   # Tier 3
   python3 tests/test_lcd_hardware.py
   python3 tests/test_lcd_integration.py
   ```

3. **OLED test pipeline**:
   ```bash
   python3 tests/test_oled_autodiscover.py
   python3 tests/test_oled_hardware.py
   python3 tests/test_oled_render.py
   python3 tests/test_oled_integration.py
   ```

4. **Full regression**:
   ```bash
   bash scripts/run_full_test_suite.sh
   ```

## Verification Scripts
| Script | Purpose |
|--------|---------|
| `scripts/verify_i2c.sh` | I2C bus health check (runs on Orange Pi) |
| `scripts/verify_lcd.sh` | Full LCD verification pipeline |
| `scripts/run_remote_tests.sh` | Run test suite via SSH from dev machine |

## Logging
- All tests log to stdout with timestamps via `utils.helpers.setup_logger`
- On Orange Pi, redirect to file: `python3 test.py 2>&1 | tee -a /var/log/tinytrade-test.log`

## Headless Verification
If no hardware is connected, verify that:
- `get_lcd_device()` returns None
- `get_oled_device()` returns None  
- `main.py` starts without crashing (all schedule callbacks handle None gracefully)
