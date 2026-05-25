import requests
import json
import time
from config import YAHOO_FINANCE_URL, US_INDICES_CONFIG, US_STOCKS, NSE_CACHE_TTL
from config import CRYPTO_SYMBOLS
from utils.helpers import setup_logger, is_us_market_open
from database.db import update_market_data, update_nse_cache, get_nse_cache

logger = setup_logger("USMarketsFetcher")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json,text/plain,*/*",
})


def _fetch_yahoo_quote(yahoo_symbol, cache_key):
    cached = get_nse_cache(cache_key)
    now = int(time.time())
    if cached and (now - cached['updated_at']) < NSE_CACHE_TTL:
        logger.info("Using cached %s (age: %ds)", cache_key, now - cached['updated_at'])
        try:
            return json.loads(cached['data'])
        except (ValueError, TypeError):
            pass

    url = YAHOO_FINANCE_URL % yahoo_symbol
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        update_nse_cache(cache_key, json.dumps(data))
        return data
    except Exception as e:
        logger.error("Yahoo fetch error for %s: %s", yahoo_symbol, e)
        if cached:
            try:
                return json.loads(cached['data'])
            except (ValueError, TypeError):
                pass
    return None


def fetch_us_market_data():
    if not is_us_market_open():
        logger.info("US market closed - skipping fetch")
        return

    logger.info("Fetching US market data...")

    for idx in US_INDICES_CONFIG:
        raw = _fetch_yahoo_quote(idx["yahoo"], "us_idx_" + idx["yahoo"])
        if raw is None:
            continue
        try:
            meta = raw["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            change_pct = meta.get("regularMarketChangePercent", 0)
            price = round(float(price), 2)
            change_pct = round(float(change_pct), 2)
            update_market_data(idx["symbol"], price, change_pct)
            logger.info("US index %s: %.2f (%.2f%%)", idx["display"], price, change_pct)
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error("Failed to parse %s: %s", idx["yahoo"], e)

    for stock in US_STOCKS:
        raw = _fetch_yahoo_quote(stock["yahoo"], "us_stk_" + stock["yahoo"])
        if raw is None:
            continue
        try:
            meta = raw["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            change_pct = meta.get("regularMarketChangePercent", 0)
            price = round(float(price), 2)
            change_pct = round(float(change_pct), 2)
            update_market_data(stock["symbol"], price, change_pct)
            logger.info("US stock %s: %.2f (%.2f%%)", stock["yahoo"], price, change_pct)
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error("Failed to parse %s: %s", stock["yahoo"], e)
