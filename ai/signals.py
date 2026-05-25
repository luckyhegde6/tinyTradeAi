from database.db import get_recent_sentiment, get_market_data, insert_alert, update_ai_suggestion, get_marquee_stocks
from utils.helpers import setup_logger
from api.telegram import send_alert_to_telegram

logger = setup_logger("SignalsAI")

_SUGGESTION_SYMBOLS = ["BTC", "ETH", "US_SPY", "US_QQQ", "US_AAPL", "US_MSFT", "US_NVDA", "NIFTY", "NIFTYBANK"]


def _get_vibe():
    sentiments = get_recent_sentiment(limit=10)
    if not sentiments:
        return "NEUTRAL", 0.0
    avg_score = sum(s["sentiment_score"] for s in sentiments) / len(sentiments)
    if avg_score > 0.2:
        return "BULLISH", avg_score
    elif avg_score < -0.2:
        return "BEARISH", avg_score
    return "NEUTRAL", avg_score


def _suggest(symbol, price, change_24h, vibe, vibe_score):
    if price is None or change_24h is None:
        update_ai_suggestion(symbol, "HOLD", 0.0, "No data")
        return

    if abs(change_24h) < 0.5:
        update_ai_suggestion(symbol, "HOLD", 0.5, "Stable price, no action")
        return

    if change_24h > 3.0 and vibe == "BULLISH":
        update_ai_suggestion(symbol, "BUY", min(0.9, 0.5 + abs(vibe_score)),
                             "Strong uptrend + bullish sentiment")
        return
    if change_24h < -3.0 and vibe == "BEARISH":
        update_ai_suggestion(symbol, "SELL", min(0.9, 0.5 + abs(vibe_score)),
                             "Sharp drop + bearish sentiment")
        return
    if change_24h > 5.0:
        update_ai_suggestion(symbol, "HOLD", 0.7,
                             "Overextended upside, wait for pullback")
        return
    if change_24h < -5.0:
        update_ai_suggestion(symbol, "BUY", 0.7,
                             "Oversold bounce potential")
        return

    if change_24h > 0:
        update_ai_suggestion(symbol, "HOLD", 0.4, "Mild uptrend, hold positions")
    else:
        update_ai_suggestion(symbol, "HOLD", 0.4, "Mild downtrend, wait for signal")


def generate_signals():
    logger.info("Generating aggregated signals...")

    vibe, vibe_score = _get_vibe()
    logger.info("Market vibe: %s (%.2f)", vibe, vibe_score)

    for sym in _SUGGESTION_SYMBOLS:
        data = get_market_data(sym)
        if data:
            price = data.get("price")
            change = data.get("change_24h")
            _suggest(sym, price, change, vibe, vibe_score)
            logger.info("Suggestion for %s: checked (price=%.2f, chg=%.2f%%)", sym, price or 0, change or 0)
        else:
            update_ai_suggestion(sym, "HOLD", 0.0, "No price data")
            logger.info("Suggestion for %s: no data", sym)

    # Process NSE marquee stocks (top 10)
    stocks = get_marquee_stocks()[:10]
    for stock in stocks:
        nse_sym = "NSE_" + stock['symbol']
        price = stock.get('last_price')
        change = stock.get('per_change')
        if price is not None and change is not None:
            _suggest(nse_sym, price, change, vibe, vibe_score)
            logger.info("NSE suggestion for %s: checked (price=%.2f, chg=%.2f%%)", nse_sym, price, change)
        else:
            update_ai_suggestion(nse_sym, "HOLD", 0.0, "No NSE stock data")
            logger.info("NSE suggestion for %s: no data", nse_sym)

    # Legacy divergence check
    sentiments = get_recent_sentiment(limit=10)
    if sentiments:
        avg_score = sum(s["sentiment_score"] for s in sentiments) / len(sentiments)
        btc_data = get_market_data("BTC")
        if btc_data:
            btc_change = btc_data.get("change_24h", 0)
            if vibe == "BULLISH" and btc_change < -5.0:
                msg = "Market sentiment BULLISH, but BTC is dropping > 5%%!"
                insert_alert("MARKET", "DIVERGENCE", msg)
                logger.warning("SIGNAL DIVERGENCE: %s", msg)
                send_alert_to_telegram("Divergence Alert: %s" % msg)
            elif vibe == "BEARISH" and btc_change > 5.0:
                msg = "Market sentiment BEARISH, but BTC is pumping > 5%%!"
                insert_alert("MARKET", "DIVERGENCE", msg)
                logger.warning("SIGNAL DIVERGENCE: %s", msg)
                send_alert_to_telegram("Divergence Alert: %s" % msg)

    return vibe
