from database.db import get_recent_sentiment, get_market_data, insert_alert
from utils.helpers import setup_logger
from api.telegram import send_alert_to_telegram

logger = setup_logger("SignalsAI")

def generate_signals():
    """
    A lightweight rule engine that combines sentiment and price data 
    to output overall market signals.
    """
    logger.info("Generating aggregated signals...")
    
    # Example logic: If overall sentiment is strongly bullish, 
    # but BTC is crashing, emit a 'DIVERGENCE' alert.
    
    sentiments = get_recent_sentiment(limit=10)
    if not sentiments:
        return
        
    avg_score = sum(s["sentiment_score"] for s in sentiments) / len(sentiments)
    
    # Determine overall news vibe
    if avg_score > 0.2:
        market_vibe = "BULLISH"
    elif avg_score < -0.2:
        market_vibe = "BEARISH"
    else:
        market_vibe = "MIXED"
        
    # Get BTC as a bellwether
    btc_data = get_market_data("BTC")
    
    if btc_data:
        btc_change = btc_data.get("change_24h", 0)
        
        # Basic Divergence Check
        if market_vibe == "BULLISH" and btc_change < -5.0:
            msg = "Market sentiment BULLISH, but BTC is dropping > 5%!"
            insert_alert("MARKET", "DIVERGENCE", msg)
            logger.warning(f"SIGNAL DIVERGENCE: {msg}")
            send_alert_to_telegram(f"Divergence Alert: {msg}")
            
        elif market_vibe == "BEARISH" and btc_change > 5.0:
            msg = "Market sentiment BEARISH, but BTC is pumping > 5%!"
            insert_alert("MARKET", "DIVERGENCE", msg)
            logger.warning(f"SIGNAL DIVERGENCE: {msg}")
            send_alert_to_telegram(f"Divergence Alert: {msg}")
            
    return market_vibe
