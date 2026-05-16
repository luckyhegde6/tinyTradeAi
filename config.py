import os
from dotenv import load_dotenv

load_dotenv()

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tinytrade.db")

# API Endpoints
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
NSE_BASE_URL = "https://www.nseindia.com"

# RSS Feeds for Sentiment Analysis
NEWS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664" # Finance
]

# Tracked Assets
CRYPTO_SYMBOLS = ["bitcoin", "ethereum", "solana"]
# For NSE, we will track specific symbols or indices like NIFTY 50
NSE_INDICES = ["NIFTY 50", "NIFTY BANK"]

# Polling Intervals (in seconds)
# Keeping them reasonable to avoid rate limits and CPU overload
CRYPTO_POLL_INTERVAL = 60
STOCKS_POLL_INTERVAL = 300  # 5 minutes
NEWS_POLL_INTERVAL = 900    # 15 minutes

# OLED Configuration
I2C_PORT = 0
I2C_ADDRESS = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Flask API Configuration
API_HOST = "0.0.0.0"
API_PORT = 5000
