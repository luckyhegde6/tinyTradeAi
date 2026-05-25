import requests
import json

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.nseindia.com/"
})

print("Getting cookies...")
s.get("https://www.nseindia.com", timeout=15)
print("Cookies:", len(s.cookies))

print("\n--- getIndexData: All index names ---")
r = s.get("https://www.nseindia.com/api/NextApi/apiClient?functionName=getIndexData&&type=All", timeout=15)
if r.status_code == 200:
    d = r.json()
    items = d.get("data", [])
    print("Total indices:", len(items))
    for item in items:
        name = item.get("indexName", "???")
        price = item.get("last", 0)
        chg = item.get("percChange", 0)
        print("  %s | last=%.2f | percChange=%.2f%%" % (name, price, chg))
        if "BANK" in name.upper():
            print("    ^^^ THIS IS THE BANK INDEX ^^^")
else:
    print("FAIL:", r.status_code, r.text[:300])

print("\n--- getMarqueData: First 5 items ---")
r = s.get("https://www.nseindia.com/api/NextApi/apiClient?functionName=getMarqueData", timeout=15)
if r.status_code == 200:
    d = r.json()
    items = d.get("data", [])
    print("Total marquee items:", len(items))
    for item in items[:5]:
        print("  %s | ltp=%.2f | chg=%.2f | perChg=%.2f%%" % (
            item.get("symbol", "?"),
            float(item.get("lastTradedPrice", 0)),
            float(item.get("change", 0)),
            float(item.get("perChange", 0))
        ))
else:
    print("FAIL:", r.status_code, r.text[:300])
