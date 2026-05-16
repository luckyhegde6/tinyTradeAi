import time
from oled.display import get_oled_device
from oled.screens import draw_crypto_ticker, draw_stock_ticker, draw_sentiment_screen, draw_alert_screen
from utils.helpers import setup_logger

logger = setup_logger("OLED_Animations")

# Define rotation sequence
SCREENS = [
    draw_crypto_ticker,
    draw_stock_ticker,
    draw_sentiment_screen,
    draw_alert_screen
]

current_screen_idx = 0

def render_next_screen():
    global current_screen_idx
    
    device = get_oled_device()
    if not device:
        # Mock mode
        current_screen_idx = (current_screen_idx + 1) % len(SCREENS)
        return
        
    try:
        # Get the drawing function
        render_func = SCREENS[current_screen_idx]
        image = render_func()
        
        # Display it
        device.display(image)
        
        # Increment
        current_screen_idx = (current_screen_idx + 1) % len(SCREENS)
    except Exception as e:
        logger.error(f"Error rendering screen: {e}")
