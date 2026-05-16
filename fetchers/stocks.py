import requests
import json
import urllib.parse
from config import NSE_BASE_URL
from utils.helpers import setup_logger
from database.db import update_market_data

logger = setup_logger("StocksFetcher")

# Create a session to persist cookies, required for NSE API
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.nseindia.com/"
}
session.headers.update(headers)

def ensure_nse_session():
    """NSE requires cookies set from the main page before hitting APIs."""
    if not session.cookies:
        try:
            logger.info("Initializing NSE Session Cookies...")
            session.get(NSE_BASE_URL, timeout=10)
        except Exception as e:
            logger.error(f"Failed to initialize NSE session: {e}")

def fetch_nse_index(index_name="NIFTY 50"):
    """Fetches the latest data for an NSE index (e.g. NIFTY 50)."""
    ensure_nse_session()
    
    try:
        # e.g. https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050
        encoded_index = urllib.parse.quote(index_name)
        url = f"{NSE_BASE_URL}/api/equity-stockIndices?index={encoded_index}"
        
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # The first item in 'data' array is usually the index itself
        if "data" in data and len(data["data"]) > 0:
            index_data = data["data"][0]
            price = index_data.get("lastPrice", 0)
            change_pct = index_data.get("pChange", 0)
            
            # Map index name for display
            display_symbol = "NIFTY" if index_name == "NIFTY 50" else index_name.replace(" ", "")
            
            update_market_data(display_symbol, price, change_pct)
            logger.info(f"Updated {display_symbol}: {price} ({change_pct}%)")
            
    except Exception as e:
        logger.error(f"Error fetching NSE index {index_name}: {e}")

def fetch_stock_prices():
    """Main entry point for fetching all configured stocks/indices."""
    # We only fetch NIFTY 50 to keep it lightweight, but can be expanded
    fetch_nse_index("NIFTY 50")
    fetch_nse_index("NIFTY BANK")
