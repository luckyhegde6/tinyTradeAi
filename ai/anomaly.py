import math
from collections import deque
from database.db import get_market_data, insert_alert
from utils.helpers import setup_logger
from api.telegram import send_alert_to_telegram

logger = setup_logger("AnomalyAI")

# Keep a lightweight rolling history of prices in memory (max 60 points)
# For a 256MB device, standard deque is much better than a Pandas DataFrame
price_history = {}

def track_price_and_detect_anomaly(symbol, current_price):
    """
    Tracks price and detects anomalies using a Z-score based approach.
    """
    if symbol not in price_history:
        price_history[symbol] = deque(maxlen=60) # Store last 60 readings
        
    history = price_history[symbol]
    history.append(current_price)
    
    # Need at least 10 data points to calculate a meaningful Z-score
    if len(history) < 10:
        return False, None
        
    # Calculate mean and standard deviation (pure Python, no numpy needed)
    n = len(history)
    mean = sum(history) / n
    variance = sum((x - mean) ** 2 for x in history) / n
    std_dev = math.sqrt(variance)
    
    if std_dev == 0:
        return False, None
        
    # Calculate Z-score
    z_score = (current_price - mean) / std_dev
    
    # Threshold for anomaly (e.g. > 3 std devs = highly unusual)
    threshold = 3.0
    
    is_anomaly = abs(z_score) > threshold
    
    if is_anomaly:
        direction = "SPIKE" if z_score > 0 else "CRASH"
        message = "%s price %s! Z-Score: %.2f (Current: %s, Mean: %.2f)" % (symbol, direction, z_score, current_price, mean)
        
        # Avoid duplicate alerts in a short span by checking the last value (naive approach)
        # More robust approach would track alert timestamps
        insert_alert(symbol, "VOLATILITY", message)
        logger.warning("ANOMALY DETECTED: %s" % message)
        send_alert_to_telegram("Volatility Anomaly: %s" % message)
        
    return is_anomaly, z_score

def check_all_assets_for_anomalies():
    """Reads latest prices from DB and checks them against history."""
    logger.info("Checking for price anomalies...")
    data = get_market_data() # Gets all current prices
    
    for row in data:
        symbol = row["symbol"]
        price = row["price"]
        track_price_and_detect_anomaly(symbol, price)
