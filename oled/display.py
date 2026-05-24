from config import I2C_PORT, I2C_ADDRESS
from utils.helpers import setup_logger

logger = setup_logger("OLED_Init")

_device = None


def get_oled_device():
    """Initializes and returns the SSD1306 OLED device singleton."""
    global _device
    if _device is None:
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import ssd1306
            logger.info("Initializing OLED on I2C Port %d, Address 0x%02X",
                        I2C_PORT, I2C_ADDRESS)
            serial = i2c(port=I2C_PORT, address=I2C_ADDRESS)
            _device = ssd1306(serial)
            logger.info("OLED initialized successfully.")
        except ImportError:
            logger.warning("luma.oled not installed. Running HEADLESS (no OLED).")
        except Exception as e:
            logger.error("Failed to initialize OLED: %s", e)
            logger.warning("Running in HEADLESS mode (no physical display).")
    return _device
