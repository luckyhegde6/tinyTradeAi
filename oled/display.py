from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from config import I2C_PORT, I2C_ADDRESS
from utils.helpers import setup_logger

logger = setup_logger("OLED_Init")

_device = None

def get_oled_device():
    """Initializes and returns the SSD1306 OLED device singleton."""
    global _device
    if _device is None:
        try:
            logger.info(f"Initializing OLED on I2C Port {I2C_PORT}, Address 0x{I2C_ADDRESS:02X}")
            serial = i2c(port=I2C_PORT, address=I2C_ADDRESS)
            _device = ssd1306(serial)
            logger.info("OLED initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize OLED: {e}")
            logger.warning("Running in HEADLESS mode (no physical display).")
            # We return None, caller must handle it gracefully
    return _device
