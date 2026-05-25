import sqlite3
c = sqlite3.connect("/opt/tinyTradeAi/tinytrade.db")
c.row_factory = sqlite3.Row
rows = c.execute("SELECT * FROM market_data").fetchall()
if rows:
    for r in rows:
        d = dict(r)
        print("  %s: price=%.2f change=%.2f%%" % (d["symbol"], d["price"], d.get("change_24h", 0)))
else:
    print("  No market data found!")
c.close()
