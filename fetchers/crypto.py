import requests
from config import COINGECKO_API_URL, CRYPTO_SYMBOLS
from utils.helpers import setup_logger
from database.db import update_market_data

logger = setup_logger("CryptoFetcher")

def fetch_crypto_prices():
    """Fetches latest prices from CoinGecko."""
    try:
        symbols = ",".join(CRYPTO_SYMBOLS)
        params = {
            "ids": symbols,
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        response = requests.get(COINGECKO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for symbol, info in data.items():
            price = info.get("usd", 0)
            change = info.get("usd_24h_change", 0)
            
            # Map 'bitcoin' to 'BTC' for display purposes
            display_symbol = symbol.upper()
            if symbol == "bitcoin": display_symbol = "BTC"
            elif symbol == "ethereum": display_symbol = "ETH"
            elif symbol == "solana": display_symbol = "SOL"
            
            update_market_data(display_symbol, price, change)
            logger.info("Updated %s: $%s (%.2f%%)" % (display_symbol, price, change))
            
    except Exception as e:
        logger.error("Error fetching crypto prices: %s" % e)
