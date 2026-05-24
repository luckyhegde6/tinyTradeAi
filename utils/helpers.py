import logging
import os

_LOG_DIR = "/var/log/tinytrade"


def setup_logger(name, log_to_file=False):
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
                logpath = os.path.join(_LOG_DIR, "%s.log" % name)
                fh = logging.FileHandler(logpath)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(fmt)
                logger.addHandler(fh)
            except (OSError, PermissionError):
                logger.warning("Cannot write to %s - file logging disabled", _LOG_DIR)

    return logger


def format_price(price):
    if price >= 1000:
        return "%s" % format(price, ",.0f")
    elif price >= 1:
        return "%.2f" % price
    else:
        return "%.4f" % price
