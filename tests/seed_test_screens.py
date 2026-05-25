import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["FLASK_ENV"] = "testing"

from database.db import (
    init_db, update_market_data, update_marquee_stocks,
    update_analysis_data, get_market_data, get_marquee_stocks,
    get_analysis_data, update_ai_suggestion
)

init_db()

print("=== Seeding test screen data ===")

# Market data (indices + crypto + US)
market_seeds = [
    ("NIFTY", 22456.75, 0.45),
    ("NIFTYBANK", 48234.10, -0.12),
    ("BTC", 67500.00, 2.50),
    ("ETH", 3450.00, -1.20),
    ("US_SPY", 5432.10, 0.32),
    ("US_DIA", 39876.50, -0.15),
    ("US_QQQ", 19234.80, 0.78),
    ("US_AAPL", 198.45, 1.23),
    ("US_MSFT", 425.60, -0.45),
    ("US_GOOGL", 167.80, 0.56),
    ("US_AMZN", 198.30, 0.89),
    ("US_NVDA", 890.20, 2.45),
]
for sym, price, chg in market_seeds:
    update_market_data(sym, price, chg)
    print("  market_data: %s = %.2f (%.2f%%)" % (sym, price, chg))

# Marquee stocks (ticker tape)
marquee_seeds = [
    {"symbol": "RELIANCE", "lastTradedPrice": 2845.50, "perChange": 0.45},
    {"symbol": "TCS", "lastTradedPrice": 3892.10, "perChange": -0.23},
    {"symbol": "HDFCBANK", "lastTradedPrice": 1675.30, "perChange": 0.78},
    {"symbol": "INFY", "lastTradedPrice": 1570.00, "perChange": 1.20},
    {"symbol": "ICICIBANK", "lastTradedPrice": 1098.60, "perChange": -0.34},
    {"symbol": "BHARTIARTL", "lastTradedPrice": 892.30, "perChange": 0.56},
    {"symbol": "SBIN", "lastTradedPrice": 765.40, "perChange": -0.15},
    {"symbol": "WIPRO", "lastTradedPrice": 432.10, "perChange": 0.89},
    {"symbol": "ITC", "lastTradedPrice": 298.75, "perChange": -0.45},
    {"symbol": "LT", "lastTradedPrice": 3456.20, "perChange": 1.10},
]
update_marquee_stocks(marquee_seeds)
print("  marquee_stocks: %d items" % len(marquee_seeds))

# Most active securities
update_analysis_data("most_active", json.dumps([
    {"symbol": "RELIANCE", "ltp": 2845.50, "perChange": 0.45},
    {"symbol": "TCS", "ltp": 3892.10, "perChange": -0.23},
    {"symbol": "HDFCBANK", "ltp": 1675.30, "perChange": 0.78},
    {"symbol": "INFY", "ltp": 1570.00, "perChange": 1.20},
    {"symbol": "ICICIBANK", "ltp": 1098.60, "perChange": -0.34},
]))
print("  most_active: 5 items")

# Gainers
update_analysis_data("gainers", json.dumps([
    {"symbol": "INFY", "ltp": 1570.00, "perChange": 2.30},
    {"symbol": "LT", "ltp": 3456.20, "perChange": 1.85},
    {"symbol": "WIPRO", "ltp": 432.10, "perChange": 1.56},
    {"symbol": "HINDALCO", "ltp": 623.40, "perChange": 1.22},
    {"symbol": "TATAMOTORS", "ltp": 895.30, "perChange": 0.95},
]))
print("  gainers: 5 items")

# Losers
update_analysis_data("losers", json.dumps([
    {"symbol": "MARUTI", "ltp": 10230.00, "perChange": -1.85},
    {"symbol": "BHARTIARTL", "ltp": 892.30, "perChange": -1.23},
    {"symbol": "ITC", "ltp": 298.75, "perChange": -0.89},
    {"symbol": "TCS", "ltp": 3892.10, "perChange": -0.23},
    {"symbol": "ICICIBANK", "ltp": 1098.60, "perChange": -0.34},
]))
print("  losers: 5 items")

# AI suggestions
suggestions = [
    ("BTC", "BUY", 0.72, "Strong uptrend + bullish sentiment"),
    ("ETH", "HOLD", 0.50, "Mild downtrend, wait for signal"),
    ("US_QQQ", "BUY", 0.65, "Strong uptrend + bullish sentiment"),
    ("US_AAPL", "HOLD", 0.40, "Stable price, no action"),
    ("US_NVDA", "BUY", 0.85, "Strong uptrend + bullish sentiment"),
    ("NIFTY", "HOLD", 0.50, "Stable index, no action"),
    ("NIFTYBANK", "HOLD", 0.40, "Mild downtrend, wait"),
    ("NSE_RELIANCE", "BUY", 0.72, "Strong uptrend + bullish"),
    ("NSE_TCS", "HOLD", 0.50, "Stable price, no action"),
    ("NSE_HDFCBANK", "BUY", 0.65, "Strong uptrend + bullish"),
    ("NSE_INFY", "HOLD", 0.60, "Mild uptrend, hold"),
    ("NSE_ICICIBANK", "SELL", 0.55, "Sharp drop + bearish"),
    ("NSE_BHARTIARTL", "BUY", 0.70, "Oversold bounce"),
]
for sym, sug, conf, reason in suggestions:
    update_ai_suggestion(sym, sug, conf, reason)
print("  ai_suggestions: %d items" % len(suggestions))

print()
print("=== Verification ===")
print("  market_data: %d records" % len(get_market_data()))
print("  marquee_stocks: %d records" % len(get_marquee_stocks()))
print("  most_active: %d records" % len(get_analysis_data("most_active")))
print("  gainers: %d records" % len(get_analysis_data("gainers")))
print("  losers: %d records" % len(get_analysis_data("losers")))
print()
print("Test data seeded. Stop tinytrade service, run this script, then restart.")
print("Screens will show: NSE (market hours) + US (market hours) + crypto + AI + base")
