import logging
import os

_LOG_DIR = "/var/log/tinytrade"


def setup_logger(name, log_to_file=False):
    """Sets up a standardized logger.

    Args:
        name: Logger name (e.g. "LCD_Init", "I2C_Scanner").
        log_to_file: If True, also writes to /var/log/tinytrade/<name>.log
                      (useful on Orange Pi for persistent debugging).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

        if log_to_file:
            try:
                os.makedirs(_LOG_DIR, exist_ok=True)
                fh = logging.FileHandler(os.path.join(_LOG_DIR, f"{name}.log"))
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(fmt)
                logger.addHandler(fh)
            except (OSError, PermissionError):
                logger.warning("Cannot write to %s — file logging disabled", _LOG_DIR)

    return logger

def format_price(price):
    """Formats a price string appropriately."""
    if price >= 1000:
        return f"{price:,.0f}"
    elif price >= 1:
        return f"{price:.2f}"
    else:
        return f"{price:.4f}"
