from PIL import Image, ImageDraw, ImageFont
from config import OLED_WIDTH, OLED_HEIGHT
from database.db import get_market_data, get_recent_sentiment, get_recent_alerts, get_marquee_stocks
from database.db import get_analysis_data, get_ai_suggestions
from utils.helpers import format_price

# Try to load a default font
try:
    font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    font_small = ImageFont.truetype("DejaVuSans.ttf", 11)
except IOError:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

def create_blank_image():
    return Image.new("1", (OLED_WIDTH, OLED_HEIGHT), "black")

def draw_crypto_ticker():
    img = create_blank_image()
    draw = ImageDraw.Draw(img)
    
    btc = get_market_data("BTC")
    eth = get_market_data("ETH")
    
    # Header
    draw.text((0, 0), "CRYPTO LIVE", fill="white", font=font_small)
    draw.line((0, 14, OLED_WIDTH, 14), fill="white")
    
    y = 20
    for data in [btc, eth]:
        if data:
            sym = data['symbol']
            prc = format_price(data['price'])
            chg = data.get('change_24h', 0)
            
            # Up/Down indicator
            arr = "UP" if chg >= 0 else "DN"
            text = "%s: $%s %s" % (sym, prc, arr)
            draw.text((0, y), text, fill="white", font=font_small)
        y += 18
        
    return img

def draw_stock_ticker():
    img = create_blank_image()
    draw = ImageDraw.Draw(img)
    
    nifty = get_market_data("NIFTY")
    bank = get_market_data("NIFTYBANK")
    
    draw.text((0, 0), "INDIAN MARKETS", fill="white", font=font_small)
    draw.line((0, 14, OLED_WIDTH, 14), fill="white")
    
    y = 20
    for data in [nifty, bank]:
        if data:
            sym = data['symbol']
            prc = format_price(data['price'])
            chg = data.get('change_24h', 0)
            arr = "+" if chg >= 0 else ""
            draw.text((0, y), "%s: %s" % (sym, prc), fill="white", font=font_small)
            draw.text((0, y+10), "Chg: %s%.2f%%" % (arr, chg), fill="white", font=font_small)
        else:
            draw.text((0, y), "NIFTY: ---", fill="white", font=font_small)
            draw.text((0, y+10), "Market closed", fill="white", font=font_small)
        y += 22
        
    return img

def draw_sentiment_screen():
    img = create_blank_image()
    draw = ImageDraw.Draw(img)
    
    recent = get_recent_sentiment(1)
    
    draw.text((0, 0), "AI SENTIMENT", fill="white", font=font_small)
    draw.line((0, 14, OLED_WIDTH, 14), fill="white")
    
    if recent:
        item = recent[0]
        label = item['label']
        score = item['sentiment_score']
        # Shorten headline
        hl = item['headline'][:40] + "..." if len(item['headline']) > 40 else item['headline']
        
        draw.text((0, 18), "Vibe: %s" % label, fill="white", font=font_large)
        draw.text((0, 36), "Score: %.2f" % score, fill="white", font=font_small)
        
        # Simple wrapping
        draw.text((0, 50), hl[:20], fill="white", font=font_small)
    else:
        draw.text((0, 20), "No data yet.", fill="white", font=font_small)
        
    return img

def draw_welcome_screen(ip_address):
    img = create_blank_image()
    draw = ImageDraw.Draw(img)

    draw.text((10, 10), "TinyTrade AI", fill="white", font=font_large)
    draw.text((10, 32), "IP: %s" % ip_address, fill="white", font=font_small)
    draw.text((10, 48), "Loading data...", fill="white", font=font_small)

    return img


def draw_alert_screen():
    img = create_blank_image()
    draw = ImageDraw.Draw(img)
    
    alerts = get_recent_alerts(1)
    
    draw.rectangle((0, 0, OLED_WIDTH, 14), fill="white")
    draw.text((2, 0), "! ALERT !", fill="black", font=font_small)
    
    if alerts:
        a = alerts[0]
        draw.text((0, 18), a['symbol'], fill="white", font=font_large)
        draw.text((0, 36), a['alert_type'], fill="white", font=font_small)
        
        msg = a['message'][:21]
        draw.text((0, 50), msg, fill="white", font=font_small)
    else:
        draw.text((0, 20), "All systems nominal.", fill="white", font=font_small)
        
    return img


def draw_index_screen(symbol, display_name):
    img = create_blank_image()
    draw = ImageDraw.Draw(img)

    draw.text((0, 0), display_name, fill="white", font=font_small)
    draw.line((0, 14, OLED_WIDTH, 14), fill="white")

    data = get_market_data(symbol)
    if data:
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        trend = "\u2191" if change >= 0 else "\u2193"
        sign = "+" if change >= 0 else ""
        draw.text((0, 18), "%s %s" % (format_price(price), trend), fill="white", font=font_large)
        draw.text((0, 44), "Chg: %s%.2f%%" % (sign, change), fill="white", font=font_small)
    else:
        draw.text((0, 20), "Market data", fill="white", font=font_small)
        draw.text((0, 36), "unavailable", fill="white", font=font_small)

    return img


def draw_marquee_stock_screen(stock_index):
    img = create_blank_image()
    draw = ImageDraw.Draw(img)

    stocks = get_marquee_stocks()
    if stock_index < len(stocks):
        stock = stocks[stock_index]
        sym = stock['symbol']
        price = stock['last_price']
        change = stock['per_change']
        trend = "\u2191" if change >= 0 else "\u2193"
        sign = "+" if change >= 0 else ""

        draw.text((0, 0), sym, fill="white", font=font_large)
        draw.line((0, 18, OLED_WIDTH, 18), fill="white")
        draw.text((0, 24), "%s %s" % (format_price(price), trend), fill="white", font=font_large)
        draw.text((0, 50), "Chg: %s%.2f%%" % (sign, change), fill="white", font=font_small)
    else:
        draw.text((0, 10), "No stock data", fill="white", font=font_small)

    return img


def draw_analysis_item_screen(category_name, db_category, index):
    img = create_blank_image()
    draw = ImageDraw.Draw(img)

    draw.text((0, 0), category_name, fill="white", font=font_small)
    draw.line((0, 14, OLED_WIDTH, 14), fill="white")

    items = get_analysis_data(db_category)
    if index < len(items):
        item = items[index]
        sym = item.get('symbol', '?')
        price = item.get('ltp', 0)
        change = item.get('perChange', 0)
        trend = "\u2191" if change >= 0 else "\u2193"
        sign = "+" if change >= 0 else ""

        draw.text((0, 18), sym, fill="white", font=font_large)
        draw.text((0, 42), "%s %s" % (format_price(price), trend), fill="white", font=font_small)
        draw.text((0, 54), "Chg: %s%.2f%%" % (sign, change), fill="white", font=font_small)
    else:
        draw.text((0, 20), "Loading...", fill="white", font=font_small)

    return img


def draw_us_index_screen(symbol, display_name):
    img = create_blank_image()
    draw = ImageDraw.Draw(img)

    draw.text((0, 0), display_name, fill="white", font=font_small)
    draw.line((0, 14, OLED_WIDTH, 14), fill="white")

    data = get_market_data(symbol)
    if data:
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        trend = "\u2191" if change >= 0 else "\u2193"
        sign = "+" if change >= 0 else ""
        draw.text((0, 18), "US %s" % format_price(price), fill="white", font=font_large)
        draw.text((0, 44), "%s %s%.2f%%" % (trend, sign, change), fill="white", font=font_small)
    else:
        draw.text((0, 20), "US market", fill="white", font=font_small)
        draw.text((0, 36), "closed", fill="white", font=font_small)

    return img


def draw_us_stock_screen(index):
    img = create_blank_image()
    draw = ImageDraw.Draw(img)

    us_stocks = [s for s in get_market_data() if s['symbol'].startswith('US_') and not s['symbol'].startswith('US_SPY') and not s['symbol'].startswith('US_DIA') and not s['symbol'].startswith('US_QQQ')]
    if index < len(us_stocks):
        stock = us_stocks[index]
        sym = stock['symbol'].replace('US_', '')
        price = stock.get('price', 0)
        change = stock.get('change_24h', 0)
        trend = "\u2191" if change >= 0 else "\u2193"
        sign = "+" if change >= 0 else ""
        draw.text((0, 0), sym, fill="white", font=font_large)
        draw.line((0, 18, OLED_WIDTH, 18), fill="white")
        draw.text((0, 24), "%s %s" % (format_price(price), trend), fill="white", font=font_large)
        draw.text((0, 50), "Chg: %s%.2f%%" % (sign, change), fill="white", font=font_small)
    else:
        draw.text((0, 10), "No US stock data", fill="white", font=font_small)

    return img


def draw_ai_suggestion_screen(symbol):
    img = create_blank_image()
    draw = ImageDraw.Draw(img)

    draw.text((0, 0), "AI SUGGESTION", fill="white", font=font_small)
    draw.line((0, 14, OLED_WIDTH, 14), fill="white")

    suggestions = get_ai_suggestions()
    match = [s for s in suggestions if s['symbol'] == symbol]
    if match:
        s = match[0]
        sug = s['suggestion']
        conf = s['confidence']
        reason = s['reason'][:20]

        sig_color = "white"
        display_sym = symbol.replace("NSE_", "").replace("US_", "")
        draw.text((0, 18), display_sym, fill="white", font=font_large)
        draw.text((0, 38), sug, fill=sig_color, font=font_large)
        draw.text((0, 54), "Conf: %.0f%% %s" % (conf * 100, reason), fill="white", font=font_small)
    else:
        draw.text((0, 20), "No suggestions", fill="white", font=font_small)
        draw.text((0, 36), "yet", fill="white", font=font_small)

    return img
