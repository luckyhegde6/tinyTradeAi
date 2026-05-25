import logging
import os
from datetime import datetime, timedelta
from config import NSE_MARKET_OPEN_HOUR, NSE_MARKET_OPEN_MIN
from config import NSE_MARKET_CLOSE_HOUR, NSE_MARKET_CLOSE_MIN
from config import _IST_OFFSET_HOURS, _IST_OFFSET_MINUTES
from config import US_MARKET_OPEN_HOUR, US_MARKET_OPEN_MIN
from config import US_MARKET_CLOSE_HOUR, US_MARKET_CLOSE_MIN

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


def _now_ist():
    utc_now = datetime.utcnow()
    return utc_now + timedelta(hours=_IST_OFFSET_HOURS, minutes=_IST_OFFSET_MINUTES)


def is_nse_market_open():
    now = _now_ist()
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=NSE_MARKET_OPEN_HOUR, minute=NSE_MARKET_OPEN_MIN, second=0, microsecond=0)
    market_close = now.replace(hour=NSE_MARKET_CLOSE_HOUR, minute=NSE_MARKET_CLOSE_MIN, second=0, microsecond=0)
    if now < market_open or now > market_close:
        return False
    return True


def _is_edt(now_local):
    year = now_local.year
    # DST starts second Sunday of March (8th-14th)
    march_1 = datetime(year, 3, 1)
    dst_start = march_1 + timedelta(days=(7 - march_1.weekday()) % 7 + 7)
    # DST ends first Sunday of November (1st-7th)
    nov_1 = datetime(year, 11, 1)
    dst_end = nov_1 + timedelta(days=(7 - nov_1.weekday()) % 7)
    return dst_start <= now_local < dst_end


def _et_offset_hours():
    utc_now = datetime.utcnow()
    now_local = utc_now.replace()
    return -4 if _is_edt(now_local) else -5


def _now_et():
    utc_now = datetime.utcnow()
    return utc_now + timedelta(hours=_et_offset_hours())


def is_us_market_open():
    now = _now_et()
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=US_MARKET_OPEN_HOUR, minute=US_MARKET_OPEN_MIN, second=0, microsecond=0)
    market_close = now.replace(hour=US_MARKET_CLOSE_HOUR, minute=US_MARKET_CLOSE_MIN, second=0, microsecond=0)
    return market_open <= now <= market_close


def get_ip_address():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No Network"


def format_price(price):
    if price >= 1000:
        return "%s" % format(price, ",.0f")
    elif price >= 1:
        return "%.2f" % price
    else:
        return "%.4f" % price
