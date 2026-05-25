from PIL import Image, ImageDraw
from config import I2C_PORT, I2C_ADDRESS, OLED_WIDTH, OLED_HEIGHT
from utils.helpers import setup_logger

logger = setup_logger("OLED_Init")

_device = None


def get_oled_device():
    global _device
    if _device is None:
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import ssd1306
            logger.info("Initializing OLED via luma on I2C Port %d, Address 0x%02X",
                        I2C_PORT, I2C_ADDRESS)
            serial = i2c(port=I2C_PORT, address=I2C_ADDRESS)
            _device = ssd1306(serial)
            logger.info("OLED initialized successfully via luma.")
        except ImportError:
            logger.warning("luma.oled not installed. Trying simple_driver fallback...")
            try:
                from oled.simple_driver import SSD1306
                _device = SSD1306(bus=I2C_PORT, addr=I2C_ADDRESS)
                logger.info("OLED initialized successfully via simple_driver.")
            except Exception as e2:
                logger.error("simple_driver also failed: %s", e2)
                logger.warning("Running HEADLESS mode (no OLED).")
        except Exception as e:
            logger.error("Failed to initialize OLED via luma: %s", e)
            logger.warning("Running in HEADLESS mode (no physical display).")
    return _device


def reset_oled_device():
    global _device
    if _device is not None:
        try:
            _device.clear()
        except Exception:
            pass
        _device = None
    logger.info("OLED device reset (will re-init on next access)")


def test_oled():
    device = get_oled_device()
    if not device:
        return False

    try:
        img = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), 0)
        draw = ImageDraw.Draw(img)

        draw.rectangle((0, 0, OLED_WIDTH - 1, OLED_HEIGHT - 1), outline=1)
        draw.line((0, 0, OLED_WIDTH - 1, OLED_HEIGHT - 1), fill=1)
        draw.line((OLED_WIDTH - 1, 0, 0, OLED_HEIGHT - 1), fill=1)
        draw.text((10, 10), "OLED TEST", fill=1)
        draw.text((10, 25), "TinyTrade AI", fill=1)
        draw.text((10, 40), "IP: see status", fill=1)

        device.display(img)
        logger.info("OLED test pattern displayed")
        return True
    except Exception as e:
        logger.error("OLED test failed: %s", e)
        return False
