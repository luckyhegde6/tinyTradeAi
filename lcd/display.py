import smbus
from lcd.driver import PCF8574LCD, I2C_LCD_KNOWN_ADDRESSES
from config import LCD_I2C_PORT, LCD_I2C_ADDRESS, LCD_COLUMNS, LCD_ROWS
from utils.helpers import setup_logger

logger = setup_logger("LCD_Init", log_to_file=True)

_device = None
_device_bus = None


def scan_i2c_bus(bus_number=0):
    bus = smbus.SMBus(bus_number)
    found = []
    try:
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                found.append(addr)
            except (OSError, IOError):
                pass
    finally:
        bus.close()
    return found


def discover_lcd_address(bus_number=0):
    found_devices = scan_i2c_bus(bus_number)
    if not found_devices:
        logger.warning("No I2C devices found on bus %d", bus_number)
        return None
    logger.info("I2C devices found: %s", [hex(a) for a in found_devices])
    search_order = I2C_LCD_KNOWN_ADDRESSES + [a for a in found_devices if a not in I2C_LCD_KNOWN_ADDRESSES]
    test_bus = smbus.SMBus(bus_number)
    try:
        for addr in search_order:
            if addr not in found_devices:
                continue
            logger.info("Probing LCD at 0x%02X...", addr)
            try:
                lcd = PCF8574LCD(test_bus, addr, LCD_COLUMNS, LCD_ROWS)
                lcd.clear()
                lcd.set_backlight(True)
                logger.info("LCD discovered at address 0x%02X", addr)
                return addr
            except Exception:
                logger.debug("No LCD at 0x%02X", addr)
        logger.warning("No PCF8574 LCD found on bus %d", bus_number)
        return None
    finally:
        test_bus.close()


def get_lcd_device():
    global _device, _device_bus

    if _device is not None:
        return _device

    try:
        if LCD_I2C_ADDRESS != 0x00:
            addr = LCD_I2C_ADDRESS
            logger.info("Initializing LCD at configured address 0x%02X", addr)
        else:
            logger.info("LCD address not configured, auto-discovering...")
            addr = discover_lcd_address(LCD_I2C_PORT)
            if addr is None:
                logger.warning("No LCD found. Running headless.")
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

    return _device
