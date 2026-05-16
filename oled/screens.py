from PIL import Image, ImageDraw, ImageFont
from config import OLED_WIDTH, OLED_HEIGHT
from database.db import get_market_data, get_recent_sentiment, get_recent_alerts
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
            text = f"{sym}: ${prc} {arr}"
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
            text = f"{sym}: {prc}"
            draw.text((0, y), text, fill="white", font=font_small)
            draw.text((0, y+10), f"Change: {arr}{chg:.2f}%", fill="white", font=font_small)
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
        
        draw.text((0, 18), f"Vibe: {label}", fill="white", font=font_large)
        draw.text((0, 36), f"Score: {score:.2f}", fill="white", font=font_small)
        
        # Simple wrapping
        draw.text((0, 50), hl[:20], fill="white", font=font_small)
    else:
        draw.text((0, 20), "No data yet.", fill="white", font=font_small)
        
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
        
        # Word wrap naive
        msg = a['message'][:21]
        draw.text((0, 50), msg, fill="white", font=font_small)
    else:
        draw.text((0, 20), "All systems nominal.", fill="white", font=font_small)
        
    return img
