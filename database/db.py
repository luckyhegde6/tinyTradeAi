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
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def update_market_data(symbol, price, change_24h=None):
    conn = get_connection()
    cursor = conn.cursor()
    now = int(time.time())
    
    cursor.execute("""
        INSERT INTO market_data (symbol, price, change_24h, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(symbol) DO UPDATE SET
            price=excluded.price,
            change_24h=excluded.change_24h,
            updated_at=excluded.updated_at
    """, (symbol, price, change_24h, now))
    
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
