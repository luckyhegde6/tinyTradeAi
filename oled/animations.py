import time
from oled.display import get_oled_device
from oled.screens import draw_crypto_ticker, draw_sentiment_screen, draw_alert_screen
from oled.screens import draw_index_screen, draw_marquee_stock_screen, draw_analysis_item_screen
from oled.screens import draw_us_index_screen, draw_us_stock_screen, draw_ai_suggestion_screen
from utils.helpers import setup_logger, is_nse_market_open, is_us_market_open
from database.db import get_marquee_stocks, get_analysis_data, get_market_data
from config import US_INDICES_CONFIG

logger = setup_logger("OLED_Animations", log_to_file=True)

SCREENS = []
current_screen_idx = 0
_last_build_time = 0


def _make_index_screen(symbol, display_name):
    def draw():
        return draw_index_screen(symbol, display_name)
    draw.__name__ = "nse_%s" % symbol.lower()
    return draw


def _make_stock_screen(index):
    def draw():
        return draw_marquee_stock_screen(index)
    draw.__name__ = "nse_stk_%d" % index
    return draw


def _make_analysis_screen(category_name, db_category, index):
    def draw():
        return draw_analysis_item_screen(category_name, db_category, index)
    draw.__name__ = "%s_%d" % (db_category, index)
    return draw


def _make_us_index_screen(symbol, display_name):
    def draw():
        return draw_us_index_screen(symbol, display_name)
    draw.__name__ = "us_%s" % display_name.lower().replace(" ", "_").replace("&", "")
    return draw


def _make_us_stock_screen(index):
    def draw():
        return draw_us_stock_screen(index)
    draw.__name__ = "us_stk_%d" % index
    return draw


def _make_ai_suggestion_screen(symbol):
    def draw():
        return draw_ai_suggestion_screen(symbol)
    draw.__name__ = "ai_%s" % symbol.lower().replace("us_", "")
    return draw


def _market_screens():
    screens = []

    if is_nse_market_open():
        screens.append(_make_index_screen("NIFTY", "NIFTY 50"))
        screens.append(_make_index_screen("NIFTYBANK", "NIFTY BANK"))
        stocks = get_marquee_stocks()
        for i in range(len(stocks)):
            screens.append(_make_stock_screen(i))
        for cat, dbcat, label in [("MOST ACTIVE", "most_active", "most"),
                                   ("TOP GAINERS", "gainers", "gain"),
                                   ("TOP LOSERS", "losers", "lose")]:
            items = get_analysis_data(dbcat)[:5]
            for i in range(len(items)):
                screens.append(_make_analysis_screen(cat, dbcat, i))

        # NSE AI suggestion screens
        screens.append(_make_ai_suggestion_screen("NIFTY"))
        screens.append(_make_ai_suggestion_screen("NIFTYBANK"))
        for stock in stocks[:10]:
            screens.append(_make_ai_suggestion_screen("NSE_" + stock['symbol']))

    if is_us_market_open():
        for idx in US_INDICES_CONFIG:
            screens.append(_make_us_index_screen(idx["symbol"], idx["display"]))
        us_data = [s for s in get_market_data() if s['symbol'].startswith('US_') and s['symbol'] not in ('US_SPY', 'US_DIA', 'US_QQQ')]
        for i in range(len(us_data)):
            screens.append(_make_us_stock_screen(i))

        for sym in ["BTC", "ETH", "US_QQQ", "US_AAPL", "US_NVDA"]:
            screens.append(_make_ai_suggestion_screen(sym))

    return screens


def build_screens():
    global SCREENS, _last_build_time
    now = time.time()
    if now - _last_build_time < 60:
        return
    _last_build_time = now

    market = _market_screens()
    base = [draw_crypto_ticker, draw_sentiment_screen, draw_alert_screen]

    if market:
        SCREENS[:] = market + base
        logger.info("Screens built: %d market + %d base = %d total", len(market), len(base), len(SCREENS))
    else:
        SCREENS[:] = base
        logger.debug("Non-market hours: %d screens (crypto, sentiment, alerts)", len(base))


def render_next_screen():
    global current_screen_idx

    build_screens()

    if not SCREENS:
        return

    if current_screen_idx >= len(SCREENS):
        current_screen_idx = 0

    device = get_oled_device()
    if not device:
        current_screen_idx = (current_screen_idx + 1) % len(SCREENS)
        return

    try:
        render_func = SCREENS[current_screen_idx]
        image = render_func()
        device.display(image)
        current_screen_idx = (current_screen_idx + 1) % len(SCREENS)
    except Exception as e:
        logger.error("Error rendering screen: %s", e)
