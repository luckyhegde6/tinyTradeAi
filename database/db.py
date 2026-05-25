import sqlite3
import time
from config import DB_PATH
from utils.helpers import setup_logger

logger = setup_logger("Database")

def get_connection():
    # check_same_thread=False allows sharing the connection between Flask and background threads
    # For a low volume embedded app, this is acceptable, provided writes are mostly sequential
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for latest prices (both crypto and stocks)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT PRIMARY KEY,
            price REAL,
            change_24h REAL,
            updated_at INTEGER
        )
    """)
    
    # Table for sentiment analysis scores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            headline TEXT,
            sentiment_score REAL,
            label TEXT,
            timestamp INTEGER
        )
    """)
    
    # Table for anomaly alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            alert_type TEXT,
            message TEXT,
            timestamp INTEGER
        )
    """)
    
    # Table for marquee stocks (NSE ticker tape)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marquee_stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            last_price REAL,
            per_change REAL,
            updated_at INTEGER
        )
    """)

    # Table for market analysis data (most active, gainers, losers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_data (
            category TEXT PRIMARY KEY,
            data TEXT,
            updated_at INTEGER
        )
    """)

    # Table for AI-powered trading suggestions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_suggestions (
            symbol TEXT PRIMARY KEY,
            suggestion TEXT,
            confidence REAL,
            reason TEXT,
            updated_at INTEGER
        )
    """)

    # Table for NSE API response cache (15-min TTL)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nse_cache (
            key TEXT PRIMARY KEY,
            data TEXT,
            updated_at INTEGER
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def update_market_data(symbol, price, change_24h=None):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())
    
    cursor.execute("SELECT 1 FROM market_data WHERE symbol = ?", (symbol,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("UPDATE market_data SET price=?, change_24h=?, updated_at=? WHERE symbol=?",
                       (price, change_24h, now, symbol))
    else:
        cursor.execute("INSERT INTO market_data (symbol, price, change_24h, updated_at) VALUES (?, ?, ?, ?)",
                       (symbol, price, change_24h, now))
    
    conn.commit()
    conn.close()

def get_market_data(symbol=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if symbol:
        cursor.execute("SELECT * FROM market_data WHERE symbol = ?", (symbol,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    else:
        cursor.execute("SELECT * FROM market_data")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

def insert_sentiment(source, headline, score, label):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())
    
    cursor.execute("""
        INSERT INTO sentiment_history (source, headline, sentiment_score, label, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (source, headline, score, label, now))
    
    conn.commit()
    conn.close()

def get_recent_sentiment(limit=5):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sentiment_history ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_alert(symbol, alert_type, message):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())
    
    cursor.execute("""
        INSERT INTO alerts (symbol, alert_type, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (symbol, alert_type, message, now))
    
    conn.commit()
    conn.close()

def get_recent_alerts(limit=5):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_nse_cache(key, data):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())
    
    cursor.execute("SELECT 1 FROM nse_cache WHERE key = ?", (key,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("UPDATE nse_cache SET data=?, updated_at=? WHERE key=?", (data, now, key))
    else:
        cursor.execute("INSERT INTO nse_cache (key, data, updated_at) VALUES (?, ?, ?)", (key, data, now))
    
    conn.commit()
    conn.close()

def get_nse_cache(key):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM nse_cache WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_marquee_stocks(stocks_list):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())

    cursor.execute("DELETE FROM marquee_stocks")
    for stock in stocks_list:
        sym = stock.get("symbol", "?")
        price = stock.get("lastTradedPrice", 0)
        chg = stock.get("perChange", 0)
        cursor.execute(
            "INSERT INTO marquee_stocks (symbol, last_price, per_change, updated_at) VALUES (?, ?, ?, ?)",
            (sym, price, chg, now)
        )

    conn.commit()
    conn.close()


def get_marquee_stocks():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM marquee_stocks ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_analysis_data(category, data_json):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())

    cursor.execute("SELECT 1 FROM analysis_data WHERE category = ?", (category,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute("UPDATE analysis_data SET data=?, updated_at=? WHERE category=?", (data_json, now, category))
    else:
        cursor.execute("INSERT INTO analysis_data (category, data, updated_at) VALUES (?, ?, ?)", (category, data_json, now))

    conn.commit()
    conn.close()


def get_analysis_data(category):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM analysis_data WHERE category = ?", (category,))
    row = cursor.fetchone()
    conn.close()
    if row:
        import json
        try:
            return json.loads(row["data"])
        except (ValueError, TypeError):
            return []
    return []


def update_ai_suggestion(symbol, suggestion, confidence, reason):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())

    cursor.execute("SELECT 1 FROM ai_suggestions WHERE symbol = ?", (symbol,))
    exists = cursor.fetchone()
    if exists:
        cursor.execute(
            "UPDATE ai_suggestions SET suggestion=?, confidence=?, reason=?, updated_at=? WHERE symbol=?",
            (suggestion, confidence, reason, now, symbol)
        )
    else:
        cursor.execute(
            "INSERT INTO ai_suggestions (symbol, suggestion, confidence, reason, updated_at) VALUES (?, ?, ?, ?, ?)",
            (symbol, suggestion, confidence, reason, now)
        )

    conn.commit()
    conn.close()


def get_ai_suggestions():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ai_suggestions ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_nse_cache():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM nse_cache")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
