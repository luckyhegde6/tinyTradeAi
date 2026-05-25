import os
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tinytrade.db")

# API Endpoints
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
NSE_BASE_URL = "https://www.nseindia.com"
NSE_INDEX_API = "https://www.nseindia.com/api/NextApi/apiClient?functionName=getIndexData&&type=All"
NSE_MARQUEE_API = "https://www.nseindia.com/api/NextApi/apiClient?functionName=getMarqueData"
NSE_MOST_ACTIVE_API = "https://www.nseindia.com/api/live-analysis-most-active-securities?index=value"
NSE_GAINERS_API = "https://www.nseindia.com/api/live-analysis-variations?index=gainers"
NSE_LOSERS_API = "https://www.nseindia.com/api/live-analysis-variations?index=loosers"

# RSS Feeds for Sentiment Analysis
NEWS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"
]

# Tracked Assets
CRYPTO_SYMBOLS = ["bitcoin", "ethereum", "solana"]
NSE_INDICES_CONFIG = [
    {"name": "NIFTY 50", "symbol": "NIFTY"},
    {"name": "NIFTY BANK", "symbol": "NIFTYBANK"},
]
US_INDICES_CONFIG = [
    {"symbol": "US_SPY", "display": "S&P 500", "yahoo": "SPY"},
    {"symbol": "US_DIA", "display": "DOW JONES", "yahoo": "DIA"},
    {"symbol": "US_QQQ", "display": "NASDAQ", "yahoo": "QQQ"},
]
US_STOCKS = [
    {"symbol": "US_AAPL", "yahoo": "AAPL"},
    {"symbol": "US_MSFT", "yahoo": "MSFT"},
    {"symbol": "US_GOOGL", "yahoo": "GOOGL"},
    {"symbol": "US_AMZN", "yahoo": "AMZN"},
    {"symbol": "US_NVDA", "yahoo": "NVDA"},
]

# Polling Intervals (in seconds)
CRYPTO_POLL_INTERVAL = 60
STOCKS_POLL_INTERVAL = 900  # 15 minutes (cached to avoid IP blocks)
ANALYSIS_POLL_INTERVAL = 3600  # 1 hour for most-active / gainers / losers
NEWS_POLL_INTERVAL = 900
US_MARKET_POLL_INTERVAL = 900  # 15 minutes
AI_SUGGESTION_INTERVAL = 300  # 5 minutes

# NSE Cache & Market Hours
NSE_CACHE_TTL = 900  # 15 seconds
NSE_MARKET_OPEN_HOUR = 9
NSE_MARKET_OPEN_MIN = 0
NSE_MARKET_CLOSE_HOUR = 15
NSE_MARKET_CLOSE_MIN = 30
_IST_OFFSET_HOURS = 5
_IST_OFFSET_MINUTES = 30

# US Market Hours (NYSE/NASDAQ: 9:30-16:00 ET)
US_MARKET_OPEN_HOUR = 9
US_MARKET_OPEN_MIN = 30
US_MARKET_CLOSE_HOUR = 16
US_MARKET_CLOSE_MIN = 0
# Yahoo Finance API
YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1d&interval=1d"

# OLED Configuration (SSD1306)
I2C_PORT = 0
I2C_ADDRESS = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 64

# LCD Configuration (PCF8574 I2C Backpack 16x2)
LCD_I2C_PORT = 0
LCD_I2C_ADDRESS = 0x00  # Set to 0x00 for auto-discovery; known addresses: 0x27, 0x3F
LCD_COLUMNS = 16
LCD_ROWS = 2

# Flask API Configuration
API_HOST = "0.0.0.0"
API_PORT = 5000
