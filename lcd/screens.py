import socket
from datetime import datetime, timedelta

from lcd.display import get_lcd_device
from database.db import get_market_data, get_recent_sentiment, get_recent_alerts, get_analysis_data, get_ai_suggestions
from utils.helpers import format_price, setup_logger

logger = setup_logger("LCD_Screens", log_to_file=True)

_marquee_offset = 0

_NSE_OPEN_HOUR = 9
_NSE_OPEN_MIN = 15
_NSE_CLOSE_HOUR = 15
_NSE_CLOSE_MIN = 30
_IST_OFFSET = timedelta(hours=5, minutes=30)
_NSE_WEEKDAYS = range(0, 5)


def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/A"


def _is_nse_market_open():
    now_utc = datetime.utcnow()
    ist_now = now_utc + _IST_OFFSET
    if ist_now.weekday() not in _NSE_WEEKDAYS:
        return False
    market_open = ist_now.replace(hour=_NSE_OPEN_HOUR, minute=_NSE_OPEN_MIN, second=0, microsecond=0)
    market_close = ist_now.replace(hour=_NSE_CLOSE_HOUR, minute=_NSE_CLOSE_MIN, second=0, microsecond=0)
    return market_open <= ist_now <= market_close


def _build_marquee_text():
    parts = []
    symbols = ["NIFTY", "NIFTYBANK", "BTC", "ETH", "SOL"]
    for sym in symbols:
        data = get_market_data(sym)
        if data:
            price = format_price(data["price"])
            chg = data.get("change_24h", 0)
            arrow = "^" if chg >= 0 else "v"
            parts.append("%s %s %s" % (sym, price, arrow))
    if not parts:
        return "  No market data yet  "
    return " | ".join(parts)


def render_time_ip():
    device = get_lcd_device()
    if not device:
        return
    try:
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        ip = _get_local_ip()
        device.write_line(time_str, 0)
        device.write_line("IP %s" % ip, 1)
    except Exception as e:
        logger.error("Time/IP render error: %s", e)


def render_nse_market_status():
    device = get_lcd_device()
    if not device:
        return
    try:
        is_open = _is_nse_market_open()
        status = "OPEN" if is_open else "CLOSED"
        now_utc = datetime.utcnow()
        ist_now = now_utc + _IST_OFFSET
        time_str = ist_now.strftime("%H:%M")
        device.write_line("NSE Market: %s" % status, 0)
        device.write_line("IST %s" % time_str, 1)
    except Exception as e:
        logger.error("NSE market render error: %s", e)


def render_stock_marquee():
    global _marquee_offset
    device = get_lcd_device()
    if not device:
        return
    try:
        full_text = _build_marquee_text()
        if len(full_text) <= 16:
            device.write_line(full_text, 0)
            device.write_line("", 1)
            return
        wrapped = full_text + "   " + full_text
        offset = _marquee_offset % len(full_text)
        visible = wrapped[offset:offset + 32]
        line0 = visible[:16]
        line1 = visible[16:32] if len(visible) > 16 else ""
        device.write_line(line0, 0)
        device.write_line(line1, 1)
        _marquee_offset += 1
    except Exception as e:
        logger.error("Marquee render error: %s", e)


def render_crypto_ticker():
    device = get_lcd_device()
    if not device:
        return
    try:
        btc = get_market_data("BTC")
        eth = get_market_data("ETH")
        if btc:
            prc = format_price(btc["price"])
            chg = btc.get("change_24h", 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line("BTC $%s %s" % (prc, arr), 0)
        if eth:
            prc = format_price(eth["price"])
            chg = eth.get("change_24h", 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line("ETH $%s %s" % (prc, arr), 1)
    except Exception as e:
        logger.error("Crypto render error: %s", e)


def render_stock_ticker():
    device = get_lcd_device()
    if not device:
        return
    try:
        nifty = get_market_data("NIFTY")
        bank = get_market_data("NIFTYBANK")
        if nifty:
            prc = format_price(nifty["price"])
            chg = nifty.get("change_24h", 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line("NIFTY %s %s" % (prc, arr), 0)
        if bank:
            prc = format_price(bank["price"])
            chg = bank.get("change_24h", 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line("BANK %s %s" % (prc, arr), 1)
    except Exception as e:
        logger.error("Stock render error: %s", e)


def render_sentiment():
    device = get_lcd_device()
    if not device:
        return
    try:
        recent = get_recent_sentiment(1)
        if recent:
            item = recent[0]
            label = item["label"]
            hl = item["headline"]
            device.write_line("AI: %s" % label, 0)
            hl = hl[:16] if len(hl) > 16 else hl
            device.write_line("%s" % hl, 1)
        else:
            device.write_line("AI Sentiment:", 0)
            device.write_line("No data yet", 1)
    except Exception as e:
        logger.error("Sentiment render error: %s", e)


def render_alert():
    device = get_lcd_device()
    if not device:
        return
    try:
        alerts = get_recent_alerts(1)
        if alerts:
            a = alerts[0]
            device.write_line("! %s" % a["symbol"], 0)
            msg = a["message"][:16] if len(a["message"]) > 16 else a["message"]
            device.write_line("%s" % msg, 1)
        else:
            device.write_line("All nominal", 0)
            device.write_line("No alerts", 1)
    except Exception as e:
        logger.error("Alert render error: %s", e)


def _render_analysis_category(category_label, db_category, items_slice=0):
    device = get_lcd_device()
    if not device:
        return
    try:
        items = get_analysis_data(db_category)
        if items:
            idx = items_slice % len(items)
            item = items[idx]
            sym = item.get('symbol', '?')
            price = format_price(item.get('ltp', 0))
            chg = item.get('perChange', 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line("%s: %s" % (category_label, sym), 0)
            device.write_line("%s %s%.2f%%" % (price, arr, abs(chg)), 1)
        else:
            device.write_line("%s: ---" % category_label, 0)
            device.write_line("No data", 1)
    except Exception as e:
        logger.error("%s render error: %s", category_label, e)


_analysis_counter = 0

def render_most_active():
    global _analysis_counter
    _analysis_counter += 1
    _render_analysis_category("ACTV", "most_active", _analysis_counter)


def render_gainers():
    global _analysis_counter
    _analysis_counter += 1
    _render_analysis_category("GAIN", "gainers", _analysis_counter)


def render_losers():
    global _analysis_counter
    _analysis_counter += 1
    _render_analysis_category("LOSE", "losers", _analysis_counter)


SCREENS = [
    render_time_ip,
    render_nse_market_status,
    render_stock_marquee,
    render_crypto_ticker,
    render_stock_ticker,
    render_sentiment,
    render_alert,
    render_most_active,
    render_gainers,
    render_losers,
]

current_screen_idx = 0


def render_us_market_status():
    device = get_lcd_device()
    if not device:
        return
    try:
        spy = get_market_data("US_SPY")
        if spy:
            prc = format_price(spy["price"])
            chg = spy.get("change_24h", 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line("S&P500 %s %s" % (prc, arr), 0)
            device.write_line("Chg %s%.2f%%" % ("+" if chg >= 0 else "", chg), 1)
        else:
            device.write_line("US Market", 0)
            device.write_line("Closed/Waiting", 1)
    except Exception as e:
        logger.error("US market render error: %s", e)


def render_us_stock_ticker():
    device = get_lcd_device()
    if not device:
        return
    try:
        stocks = [s for s in get_market_data() if s['symbol'].startswith('US_') and s['symbol'] != 'US_SPY' and s['symbol'] != 'US_DIA' and s['symbol'] != 'US_QQQ']
        if stocks:
            stock = stocks[0]
            sym = stock['symbol'].replace('US_', '')
            prc = format_price(stock["price"])
            chg = stock.get("change_24h", 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line("%s %s %s" % (sym, prc, arr), 0)
            device.write_line("Chg %s%.2f%%" % ("+" if chg >= 0 else "", chg), 1)
        else:
            device.write_line("US Stocks: ---", 0)
            device.write_line("No data", 1)
    except Exception as e:
        logger.error("US stock render error: %s", e)


def render_ai_suggestion():
    device = get_lcd_device()
    if not device:
        return
    try:
        suggestions = get_ai_suggestions()
        if suggestions:
            s = suggestions[0]
            display_sym = s['symbol'].replace("NSE_", "").replace("US_", "")
            device.write_line("%s: %s" % (display_sym, s['suggestion']), 0)
            device.write_line("Conf %.0f%% %s" % (s['confidence'] * 100, s['reason'][:10]), 1)
        else:
            device.write_line("AI Suggestions:", 0)
            device.write_line("Analyzing...", 1)
    except Exception as e:
        logger.error("AI suggestion render error: %s", e)


SCREENS = [
    render_time_ip,
    render_nse_market_status,
    render_stock_marquee,
    render_crypto_ticker,
    render_stock_ticker,
    render_sentiment,
    render_alert,
    render_most_active,
    render_gainers,
    render_losers,
    render_us_market_status,
    render_us_stock_ticker,
    render_ai_suggestion,
]

current_screen_idx = 0


def render_next_screen():
    global current_screen_idx
    device = get_lcd_device()
    if not device:
        current_screen_idx = (current_screen_idx + 1) % len(SCREENS)
        return
    try:
        SCREENS[current_screen_idx]()
        current_screen_idx = (current_screen_idx + 1) % len(SCREENS)
    except Exception as e:
        logger.error("LCD screen error: %s", e)
