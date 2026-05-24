from lcd.display import get_lcd_device
from database.db import get_market_data, get_recent_sentiment, get_recent_alerts
from utils.helpers import format_price, setup_logger

logger = setup_logger("LCD_Screens", log_to_file=True)

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
            device.write_line(f"BTC ${prc} {arr}", 0)
        if eth:
            prc = format_price(eth["price"])
            chg = eth.get("change_24h", 0)
            arr = "^" if chg >= 0 else "v"
            device.write_line(f"ETH ${prc} {arr}", 1)
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
            device.write_line(f"NIFTY {prc}", 0)
        if bank:
            prc = format_price(bank["price"])
            device.write_line(f"BANK {prc}", 1)
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
            score = item["sentiment_score"]
            device.write_line(f"AI: {label}", 0)
            hl = item["headline"][:16] if len(item["headline"]) > 16 else item["headline"]
            device.write_line(f"{hl}", 1)
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
            device.write_line(f"! {a['symbol']}", 0)
            msg = a["message"][:16] if len(a["message"]) > 16 else a["message"]
            device.write_line(f"{msg}", 1)
        else:
            device.write_line("All nominal", 0)
            device.write_line("No alerts", 1)
    except Exception as e:
        logger.error("Alert render error: %s", e)

SCREENS = [
    render_crypto_ticker,
    render_stock_ticker,
    render_sentiment,
    render_alert,
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
