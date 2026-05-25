import os
from utils.helpers import setup_logger

logger = setup_logger("GPIO")

SYSFS_GPIO = "/sys/class/gpio"

# Known GPIO pins on Orange Pi 2G-IOT 26-pin header
# RDA8810 GPIO bank A (0-31), B (32-63)
KNOWN_GPIO = {
    0: "PA0", 1: "PA1", 2: "PA2", 3: "PA3",
    4: "PB0", 5: "PB1", 6: "PB2", 7: "PB3",
    8: "PC0", 9: "PC1", 10: "PC2", 11: "PC3",
    12: "PD0", 13: "PD1", 14: "PD2", 15: "PD3",
}


def _gpio_path(pin):
    return os.path.join(SYSFS_GPIO, "gpio%d" % pin)


def _is_exported(pin):
    return os.path.isdir(_gpio_path(pin))


def list_gpios():
    result = []
    for pin, name in sorted(KNOWN_GPIO.items()):
        gpio = {"pin": pin, "name": name, "exported": _is_exported(pin)}
        if gpio["exported"]:
            try:
                with open(os.path.join(_gpio_path(pin), "direction")) as f:
                    gpio["direction"] = f.read().strip()
            except Exception:
                gpio["direction"] = "unknown"
            try:
                with open(os.path.join(_gpio_path(pin), "value")) as f:
                    gpio["value"] = int(f.read().strip())
            except Exception:
                gpio["value"] = None
        result.append(gpio)
    return result


def export_gpio(pin):
    if _is_exported(pin):
        logger.info("GPIO %d already exported", pin)
        return True
    try:
        with open(os.path.join(SYSFS_GPIO, "export"), "w") as f:
            f.write(str(pin))
        logger.info("GPIO %d exported", pin)
        return True
    except Exception as e:
        logger.error("Failed to export GPIO %d: %s", pin, e)
        return False


def unexport_gpio(pin):
    if not _is_exported(pin):
        return True
    try:
        with open(os.path.join(SYSFS_GPIO, "unexport"), "w") as f:
            f.write(str(pin))
        logger.info("GPIO %d unexported", pin)
        return True
    except Exception as e:
        logger.error("Failed to unexport GPIO %d: %s", pin, e)
        return False


def set_direction(pin, direction):
    if direction not in ("in", "out"):
        logger.error("Invalid direction '%s' (must be 'in' or 'out')", direction)
        return False
    if not _is_exported(pin):
        if not export_gpio(pin):
            return False
    try:
        with open(os.path.join(_gpio_path(pin), "direction"), "w") as f:
            f.write(direction)
        logger.info("GPIO %d direction set to %s", pin, direction)
        return True
    except Exception as e:
        logger.error("Failed to set GPIO %d direction: %s", pin, e)
        return False


def set_value(pin, value):
    if value not in (0, 1):
        logger.error("Invalid value '%s' (must be 0 or 1)", value)
        return False
    if not _is_exported(pin):
        if not export_gpio(pin):
            return False
    try:
        with open(os.path.join(_gpio_path(pin), "direction"), "r") as f:
            if f.read().strip() != "out":
                set_direction(pin, "out")
        with open(os.path.join(_gpio_path(pin), "value"), "w") as f:
            f.write(str(value))
        logger.info("GPIO %d set to %d", pin, value)
        return True
    except Exception as e:
        logger.error("Failed to set GPIO %d value: %s", pin, e)
        return False


def get_value(pin):
    if not _is_exported(pin):
        return None
    try:
        with open(os.path.join(_gpio_path(pin), "value")) as f:
            return int(f.read().strip())
    except Exception as e:
        logger.error("Failed to read GPIO %d: %s", pin, e)
        return None


def get_gpio(pin):
    gpio = {"pin": pin, "exported": _is_exported(pin)}
    if gpio["exported"]:
        try:
            with open(os.path.join(_gpio_path(pin), "direction")) as f:
                gpio["direction"] = f.read().strip()
        except Exception:
            gpio["direction"] = "unknown"
        try:
            with open(os.path.join(_gpio_path(pin), "value")) as f:
                gpio["value"] = int(f.read().strip())
        except Exception:
            gpio["value"] = None
    return gpio
