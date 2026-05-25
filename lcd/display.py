import smbus
from lcd.driver import PCF8574LCD, I2C_LCD_KNOWN_ADDRESSES
from config import LCD_I2C_PORT, LCD_I2C_ADDRESS, LCD_COLUMNS, LCD_ROWS
from utils.helpers import setup_logger

logger = setup_logger("LCD_Init", log_to_file=True)

_device = None
_device_bus = None
_init_attempted = False


def probe_lcd_address(bus_number, addr):
    bus = smbus.SMBus(bus_number)
    try:
        bus.write_byte(addr, 0x08)
        bus.close()
        return True
    except Exception:
        try:
            bus.close()
        except Exception:
            pass
        return False


def discover_lcd_address(bus_number=0):
    for addr in I2C_LCD_KNOWN_ADDRESSES:
        logger.info("Probing LCD at 0x%02X...", addr)
        if not probe_lcd_address(bus_number, addr):
            continue
        test_bus = smbus.SMBus(bus_number)
        try:
            lcd = PCF8574LCD(test_bus, addr, LCD_COLUMNS, LCD_ROWS)
            lcd.clear()
            lcd.set_backlight(True)
            logger.info("LCD discovered at address 0x%02X", addr)
            test_bus.close()
            return addr
        except Exception:
            try:
                test_bus.close()
            except Exception:
                pass
    logger.warning("No PCF8574 LCD found on bus %d", bus_number)
    return None


def get_lcd_device():
    global _device, _device_bus, _init_attempted

    if _device is not None:
        return _device
    if _init_attempted:
        return None

    try:
        if LCD_I2C_ADDRESS != 0x00:
            addr = LCD_I2C_ADDRESS
            logger.info("Initializing LCD at configured address 0x%02X", addr)
        else:
            logger.info("LCD address not configured, auto-discovering...")
            addr = discover_lcd_address(LCD_I2C_PORT)
            if addr is None:
                logger.warning("No LCD found. Running headless.")
                _init_attempted = True
                return None
            logger.info("Auto-discovered LCD at 0x%02X", addr)

        _device_bus = smbus.SMBus(LCD_I2C_PORT)
        _device = PCF8574LCD(_device_bus, addr, LCD_COLUMNS, LCD_ROWS)
        _device.clear()
        _device.write_line("TinyTrade AI", 0)
        _device.write_line("LCD Ready", 1)
        logger.info("LCD initialized successfully at 0x%02X", addr)
    except Exception as e:
        logger.error("Failed to initialize LCD: %s", e)
        logger.warning("Running HEADLESS mode (no physical LCD).")
        if _device_bus is not None:
            try:
                _device_bus.close()
            except Exception:
                pass
            _device_bus = None
        _device = None
        _init_attempted = True

    return _device


def reset_lcd_device():
    global _device, _device_bus, _init_attempted

    if _device is not None:
        try:
            _device.clear()
            _device.set_backlight(False)
            _device.close()
        except Exception:
            pass
    if _device_bus is not None:
        try:
            _device_bus.close()
        except Exception:
            pass

    _device = None
    _device_bus = None
    _init_attempted = False
    logger.info("LCD device reset (will re-init on next access)")


def clear_lcd():
    device = get_lcd_device()
    if not device:
        return False
    try:
        device.clear()
        logger.info("LCD cleared")
        return True
    except Exception as e:
        logger.error("LCD clear failed: %s", e)
        return False


def test_lcd():
    device = get_lcd_device()
    if not device:
        return False
    try:
        device.clear()
        device.set_backlight(True)
        device.write_line("LCD TEST", 0)
        device.write_line("TinyTrade AI", 1)
        logger.info("LCD test pattern displayed")
        return True
    except Exception as e:
        logger.error("LCD test failed: %s", e)
        return False
