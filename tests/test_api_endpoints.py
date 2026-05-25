#!/usr/bin/env python3
"""
API Endpoint Integration Test
Tests all REST API endpoints on the running TinyTrade service.
Connects to localhost:5000 by default, or $API_HOST:$API_PORT if set.

Usage:
  python tests/test_api_endpoints.py              # test localhost:5000
  API_HOST=192.168.0.12 python tests/test_api_endpoints.py  # test remote
"""

import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_HOST = os.environ.get("API_HOST", "localhost")
API_PORT = os.environ.get("API_PORT", "5000")
BASE = "http://%s:%s" % (API_HOST, API_PORT)

TEST_GPIO_PIN = int(os.environ.get("TEST_GPIO_PIN", "0"))

passed = 0
failed = 0
errors = []


def request(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as e:
        return 0, {"error": str(e)}


def get(path):
    return request("GET", path)


def post(path, body=None):
    return request("POST", path, body)


def put(path, body):
    return request("PUT", path, body)


def check(name, status, body, expect_status=200, extra=None):
    global passed, failed
    status_ok = status == expect_status
    if status_ok:
        if extra:
            status_ok = all(k in body for k in extra) if isinstance(body, dict) else False
        if status_ok:
            passed += 1
            print("  [PASS] %s (HTTP %d)" % (name, status))
            return True

    failed += 1
    msg = "  [FAIL] %s (HTTP %d, expected %d)" % (name, status, expect_status)
    if isinstance(body, dict) and "error" in body:
        msg += ": %s" % body["error"]
    print(msg)
    errors.append("%s: HTTP %d -> %s" % (name, status, body))
    return False


def section(title):
    print("\n%s" % title)
    print("  " + "-" * (len(title) - 2))


# ============================================================
print("=" * 60)
print("TinyTrade AI - API Endpoint Test Suite")
print("Target: %s" % BASE)
print("=" * 60)

# --- Status ---
section("1. System Status")
s, b = get("/api/status")
check("GET /api/status", s, b, extra=["status", "uptime_seconds", "displays"])
if s == 200 and "displays" in b:
    oled = b["displays"].get("oled", {})
    lcd = b["displays"].get("lcd", {})
    print("       OLED: avail=%s, screen=%d/%d" % (
        oled.get("available"), oled.get("current_screen"), len(oled.get("screens", []))))
    print("       LCD:  avail=%s, screen=%d/%d" % (
        lcd.get("available"), lcd.get("current_screen"), len(lcd.get("screens", []))))

# --- Market Data ---
section("2. Market Data")
s, b = get("/api/prices")
check("GET /api/prices", s, b)
s, b = get("/api/prices/BTC")
check("GET /api/prices/BTC", s, b)
s, b = get("/api/prices/__NONEXISTENT__")
check("GET /api/prices/{bad_sym} (expect 404)", s, b, expect_status=404)

s, b = get("/api/sentiment?limit=3")
check("GET /api/sentiment", s, b)

s, b = get("/api/alerts?limit=3")
check("GET /api/alerts", s, b)

# --- Config ---
section("3. Runtime Config")
s, b = get("/api/config")
check("GET /api/config", s, b)
old_crypto = b.get("crypto_poll_interval", 60) if s == 200 else 60

s, b = put("/api/config", {"crypto_poll_interval": 99, "screen_rotation_interval": 7})
check("PUT /api/config (valid update)", s, b, extra=["updated", "previous"])
if s == 200:
    print("       updated: %s" % b.get("updated"))
    print("       previous: %s" % b.get("previous"))

s, b = put("/api/config", {"invalid_key": 123})
check("PUT /api/config (invalid key - expect 400)", s, b, expect_status=400)

# Restore original
put("/api/config", {"crypto_poll_interval": old_crypto, "screen_rotation_interval": 5})

# --- Display - OLED ---
section("4. OLED Display Control")
s, b = post("/api/display/oled/test")
check("POST /api/display/oled/test", s, b)

s, b = post("/api/display/oled/clear")
check("POST /api/display/oled/clear", s, b)

s, b = post("/api/display/oled/reset")
check("POST /api/display/oled/reset", s, b)

s, b = post("/api/display/screen/oled", {"screen": 0})
check("POST /api/display/screen/oled (idx=0)", s, b)

s, b = post("/api/display/screen/oled", {"screen": 999})
check("POST /api/display/screen/oled (bad idx - expect 400)", s, b, expect_status=400)

# --- Display - LCD (no hardware expected) ---
section("5. LCD Display Control (no hardware)")
s, b = post("/api/display/lcd/test")
check("POST /api/display/lcd/test (expect 500)", s, b, expect_status=500)

s, b = post("/api/display/lcd/clear")
check("POST /api/display/lcd/clear (expect 500)", s, b, expect_status=500)

s, b = post("/api/display/lcd/reset")
check("POST /api/display/lcd/reset (degraded ok)", s, b)

# --- GPIO ---
section("6. GPIO Control")
s, b = get("/api/gpio")
check("GET /api/gpio", s, b, extra=["gpios"])

s, b = get("/api/gpio/%d" % TEST_GPIO_PIN)
check("GET /api/gpio/%d" % TEST_GPIO_PIN, s, b, extra=["gpio"])
was_exported = b.get("gpio", {}).get("exported", False) if s == 200 else False

# Export if not already
if not was_exported:
    s, b = post("/api/gpio/export", {"pin": TEST_GPIO_PIN})
    check("POST /api/gpio/export (pin=%d)" % TEST_GPIO_PIN, s, b)

s, b = post("/api/gpio/%d/direction" % TEST_GPIO_PIN, {"direction": "out"})
check("POST /api/gpio/%d/direction (out)" % TEST_GPIO_PIN, s, b)

s, b = post("/api/gpio/%d/value" % TEST_GPIO_PIN, {"value": 1})
check("POST /api/gpio/%d/value (1)" % TEST_GPIO_PIN, s, b)

s, b = post("/api/gpio/%d/value" % TEST_GPIO_PIN, {"value": 0})
check("POST /api/gpio/%d/value (0)" % TEST_GPIO_PIN, s, b)

s, b = post("/api/gpio/%d/direction" % TEST_GPIO_PIN, {"direction": "in"})
check("POST /api/gpio/%d/direction (in)" % TEST_GPIO_PIN, s, b)

if not was_exported:
    s, b = post("/api/gpio/unexport", {"pin": TEST_GPIO_PIN})
    check("POST /api/gpio/unexport (pin=%d)" % TEST_GPIO_PIN, s, b)

# Validation tests
s, b = post("/api/gpio/export", {"pin": "notanumber"})
check("POST /api/gpio/export (bad pin - expect 400)", s, b, expect_status=400)

s, b = post("/api/gpio/%d/direction" % TEST_GPIO_PIN, {"direction": "invalid"})
check("POST /api/gpio/%d/direction (bad dir - expect 400)" % TEST_GPIO_PIN, s, b, expect_status=400)

s, b = post("/api/gpio/%d/value" % TEST_GPIO_PIN, {"value": 99})
check("POST /api/gpio/%d/value (bad val - expect 400)" % TEST_GPIO_PIN, s, b, expect_status=400)

# --- Swagger / OpenAPI ---
section("7. API Documentation")
s, b = get("/api/openapi.json")
check("GET /api/openapi.json", s, b, extra=["openapi", "info", "paths"])
if s == 200:
    print("       %d endpoints documented" % len(b.get("paths", {})))

try:
    req = urllib.request.Request(BASE + "/api/docs")
    r = urllib.request.urlopen(req, timeout=10)
    html = r.read().decode()
    if r.status == 200 and "swagger-ui" in html:
        passed += 1
        print("  [PASS] GET /api/docs (Swagger UI) (HTTP 200)")
    else:
        failed += 1
        print("  [FAIL] GET /api/docs (Swagger UI) (HTTP %d)" % r.status)
        errors.append("GET /api/docs: HTTP %d" % r.status)
except Exception as e:
    failed += 1
    print("  [FAIL] GET /api/docs (Swagger UI): %s" % e)
    errors.append("GET /api/docs: %s" % e)

# --- Summary ---
print("\n" + "=" * 60)
total = passed + failed
print("Results: %d/%d passed, %d failed" % (passed, total, failed))
if errors:
    print("\nFailures:")
    for e in errors:
        print("  - %s" % e)
print("=" * 60)

if failed > 0:
    sys.exit(1)
