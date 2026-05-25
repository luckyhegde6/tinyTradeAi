import time
from utils.helpers import setup_logger

logger = setup_logger("DisplayManager", log_to_file=True)

_oled = None
_lcd = None
_oled_available = False
_lcd_available = False
_oled_retry_count = 0
_MAX_OLED_RETRIES = 5


def probe_oled():
    global _oled, _oled_available, _oled_retry_count
    try:
        from oled.display import get_oled_device
        _oled = get_oled_device()
        if _oled is not None:
            _oled_available = True
            _oled_retry_count = 0
            logger.info("OLED detected and initialized")
            return True
    except Exception as e:
        logger.error("OLED init error: %s", e)
    _oled_available = False
    return False


def probe_lcd():
    global _lcd, _lcd_available
    try:
        from lcd.display import get_lcd_device
        _lcd = get_lcd_device()
        if _lcd is not None:
            _lcd_available = True
            logger.info("LCD detected and initialized")
            return True
    except Exception as e:
        logger.error("LCD init error: %s", e)
    _lcd_available = False
    return False


def init_displays():
    probed = []

    for attempt in range(_MAX_OLED_RETRIES + 1):
        if probe_oled():
            probed.append("OLED")
            break
        if attempt < _MAX_OLED_RETRIES:
            delay = 2 ** attempt
            logger.warning("OLED probe attempt %d/%d failed, retrying in %ds...",
                           attempt + 1, _MAX_OLED_RETRIES + 1, delay)
            time.sleep(delay)

    if probe_lcd():
        probed.append("LCD")
    if probed:
        logger.info("Display(s) available: %s", ", ".join(probed))
    else:
        logger.warning("No displays detected. Running headless.")
    return probed


_last_lcd_check = 0
_last_oled_check = 0

def check_display_health():
    global _oled, _oled_available, _lcd, _lcd_available, _last_lcd_check, _last_oled_check

    now = time.time()

    if not _oled_available:
        if now - _last_oled_check > 60:
            _last_oled_check = now
            logger.info("Health check: OLED not available, re-probing...")
            _reset_oled_singleton()
            for attempt in range(3):
                if probe_oled():
                    logger.info("Health check: OLED recovered")
                    break
                time.sleep(1)

    if not _lcd_available:
        now = time.time()
        if now - _last_lcd_check > 300:
            _last_lcd_check = now
            from lcd.display import _init_attempted as lcd_tried
            if not lcd_tried:
                logger.info("Health check: LCD not available, first probe...")
                probe_lcd()


def _reset_oled_singleton():
    import oled.display as oled_mod
    oled_mod._device = None


def _reset_lcd_singleton():
    import lcd.display as lcd_mod
    lcd_mod._device = None
    lcd_mod._device_bus = None
    lcd_mod._init_attempted = False


def render_next_screen():
    if _oled_available:
        try:
            from oled.animations import render_next_screen as render_oled
            render_oled()
        except Exception:
            pass
    if _lcd_available:
        try:
            from lcd.screens import render_next_screen as render_lcd
            render_lcd()
        except Exception:
            pass


def show_boot_splash(ip_address, duration=5):
    if not _oled_available:
        logger.info("No OLED available for boot splash")
        return

    try:
        from oled.screens import draw_welcome_screen
        image = draw_welcome_screen(ip_address)
        _oled.display(image)
        logger.info("Boot splash displayed: IP=%s for %ds" % (ip_address, duration))
        time.sleep(duration)
    except Exception as e:
        logger.error("Boot splash error: %s" % e)


def is_oled_available():
    return _oled_available


def is_lcd_available():
    return _lcd_available


def get_oled_screen_names():
    from oled.animations import SCREENS, build_screens
    build_screens()
    return [f.__name__ for f in SCREENS]


def get_lcd_screen_names():
    from lcd.screens import SCREENS
    return [f.__name__ for f in SCREENS]


def set_oled_screen(index):
    from oled import animations as oled_anim
    oled_anim.build_screens()
    total = len(oled_anim.SCREENS)
    if 0 <= index < total:
        oled_anim.current_screen_idx = index
        logger.info("OLED screen set to index %d (%s)", index, oled_anim.SCREENS[index].__name__)
        return True
    logger.warning("Invalid OLED screen index %d (0-%d)", index, total - 1)
    return False


def set_lcd_screen(index):
    from lcd import screens as lcd_screens
    total = len(lcd_screens.SCREENS)
    if 0 <= index < total:
        lcd_screens.current_screen_idx = index
        logger.info("LCD screen set to index %d (%s)", index, lcd_screens.SCREENS[index].__name__)
        return True
    logger.warning("Invalid LCD screen index %d (0-%d)", index, total - 1)
    return False


def get_oled_screen_index():
    from oled import animations as oled_anim
    return oled_anim.current_screen_idx


def get_lcd_screen_index():
    from lcd import screens as lcd_screens
    return lcd_screens.current_screen_idx


def test_oled():
    from oled.display import test_oled as _test
    ok = _test()
    if ok:
        logger.info("OLED test triggered via API")
    return ok


def test_lcd():
    from lcd.display import test_lcd as _test
    ok = _test()
    if ok:
        logger.info("LCD test triggered via API")
    return ok


def clear_oled():
    global _oled, _oled_available
    if not _oled:
        return False
    try:
        _oled.clear()
        logger.info("OLED cleared via API")
        return True
    except Exception as e:
        logger.error("OLED clear failed: %s", e)
        return False


def clear_lcd():
    from lcd.display import clear_lcd as _clear
    return _clear()


def reset_oled():
    global _oled, _oled_available
    _reset_oled_singleton()
    _oled = None
    _oled_available = False
    logger.info("OLED reset requested")
    return probe_oled()


def reset_lcd():
    global _lcd, _lcd_available
    _reset_lcd_singleton()
    _lcd = None
    _lcd_available = False
    logger.info("LCD reset requested")
    return probe_lcd()
