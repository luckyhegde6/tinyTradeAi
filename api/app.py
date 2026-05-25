import os, time, threading
from flask import Flask, jsonify, request, render_template_string

from database.db import get_market_data, get_recent_sentiment, get_recent_alerts
from display.manager import (
    is_oled_available, is_lcd_available,
    get_oled_screen_names, get_lcd_screen_names,
    get_oled_screen_index, get_lcd_screen_index,
    set_oled_screen, set_lcd_screen,
    test_oled, test_lcd,
    clear_oled, clear_lcd,
    reset_oled, reset_lcd,
)
from utils.config_manager import get_all as get_all_config, set_many as set_config
from utils.gpio import list_gpios, get_gpio, export_gpio, unexport_gpio, set_direction, set_value
from utils.helpers import setup_logger

logger = setup_logger("API")

app = Flask(__name__)

_start_time = time.time()
_restart_requested = False


def request_restart():
    global _restart_requested
    _restart_requested = True


def is_restart_requested():
    return _restart_requested


def _get_memory_info():
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                if parts[0].rstrip(":") in ("MemTotal", "MemFree", "MemAvailable"):
                    mem[parts[0].rstrip(":")] = int(parts[1])
        return mem
    except Exception:
        return {"error": "unavailable"}


def _delayed_exit():
    time.sleep(1)
    os._exit(0)


def _get_json_body():
    body = request.get_json(force=True, silent=True)
    if not body or not isinstance(body, dict):
        return None
    return body


def _require_json(*keys):
    body = _get_json_body()
    if body is None:
        return None, jsonify({"error": "Request body must be a JSON object"}), 400
    for k in keys:
        if k not in body:
            return None, jsonify({"error": "Missing required key: '%s'" % k}), 400
    return body, None, None


# --- Status ---

@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "running",
        "device": "TinyTrade AI",
        "uptime_seconds": int(time.time() - _start_time),
        "memory_kb": _get_memory_info(),
        "displays": {
            "oled": {
                "available": is_oled_available(),
                "current_screen": get_oled_screen_index(),
                "screens": get_oled_screen_names(),
            },
            "lcd": {
                "available": is_lcd_available(),
                "current_screen": get_lcd_screen_index(),
                "screens": get_lcd_screen_names(),
            },
        },
    })


# --- Market Data ---

@app.route("/api/prices")
def api_prices():
    return jsonify(get_market_data())


@app.route("/api/prices/<symbol>")
def api_price(symbol):
    data = get_market_data(symbol.upper())
    if data is None:
        return jsonify({"error": "Symbol not found"}), 404
    return jsonify(data)


@app.route("/api/sentiment")
def api_sentiment():
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_recent_sentiment(limit))


@app.route("/api/alerts")
def api_alerts():
    limit = request.args.get("limit", 10, type=int)
    return jsonify(get_recent_alerts(limit))


# --- Config ---

@app.route("/api/config", methods=["GET"])
def api_config_get():
    return jsonify(get_all_config())


@app.route("/api/config", methods=["PUT"])
def api_config_update():
    body = _get_json_body()
    if body is None:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    allowed = {
        "crypto_poll_interval", "stocks_poll_interval", "news_poll_interval",
        "screen_rotation_interval", "oled_enabled", "lcd_enabled",
    }
    updates = {k: v for k, v in body.items() if k in allowed and v is not None}
    if not updates:
        return jsonify({"error": "No valid config keys", "valid_keys": list(allowed)}), 400

    old = set_config(updates)
    logger.info("Config updated: %s", updates)
    return jsonify({"updated": updates, "previous": old})


# --- Display Control ---

@app.route("/api/display/screen/oled", methods=["POST"])
def api_display_screen_oled():
    body, err, code = _require_json("screen")
    if err:
        return err, code
    idx = body["screen"]
    if not isinstance(idx, int):
        return jsonify({"error": "'screen' must be an integer"}), 400
    if not is_oled_available():
        return jsonify({"error": "OLED not available"}), 503
    if not set_oled_screen(idx):
        return jsonify({"error": "Invalid screen index", "max": len(get_oled_screen_names()) - 1}), 400
    return jsonify({"screen": idx, "name": get_oled_screen_names()[idx]})


@app.route("/api/display/screen/lcd", methods=["POST"])
def api_display_screen_lcd():
    body, err, code = _require_json("screen")
    if err:
        return err, code
    idx = body["screen"]
    if not isinstance(idx, int):
        return jsonify({"error": "'screen' must be an integer"}), 400
    if not is_lcd_available():
        return jsonify({"error": "LCD not available"}), 503
    if not set_lcd_screen(idx):
        return jsonify({"error": "Invalid screen index", "max": len(get_lcd_screen_names()) - 1}), 400
    return jsonify({"screen": idx, "name": get_lcd_screen_names()[idx]})


@app.route("/api/display/oled/test", methods=["POST"])
def api_display_oled_test():
    ok = test_oled()
    if not ok:
        return jsonify({"error": "OLED test failed (not available or error)"}), 500
    return jsonify({"status": "ok", "message": "OLED test pattern displayed"})


@app.route("/api/display/oled/clear", methods=["POST"])
def api_display_oled_clear():
    ok = clear_oled()
    if not ok:
        return jsonify({"error": "OLED clear failed (not available or error)"}), 500
    return jsonify({"status": "ok", "message": "OLED cleared"})


@app.route("/api/display/oled/reset", methods=["POST"])
def api_display_oled_reset():
    ok = reset_oled()
    if ok:
        return jsonify({"status": "ok", "message": "OLED reset and re-initialized"})
    return jsonify({"status": "degraded", "message": "OLED reset attempted but not available"})


@app.route("/api/display/lcd/test", methods=["POST"])
def api_display_lcd_test():
    ok = test_lcd()
    if not ok:
        return jsonify({"error": "LCD test failed (not available or error)"}), 500
    return jsonify({"status": "ok", "message": "LCD test pattern displayed"})


@app.route("/api/display/lcd/clear", methods=["POST"])
def api_display_lcd_clear():
    ok = clear_lcd()
    if not ok:
        return jsonify({"error": "LCD clear failed (not available or error)"}), 500
    return jsonify({"status": "ok", "message": "LCD cleared"})


@app.route("/api/display/lcd/reset", methods=["POST"])
def api_display_lcd_reset():
    ok = reset_lcd()
    if ok:
        return jsonify({"status": "ok", "message": "LCD reset and re-initialized"})
    return jsonify({"status": "degraded", "message": "LCD reset attempted but not available"})


# --- GPIO ---

@app.route("/api/gpio", methods=["GET"])
def api_gpio_list():
    return jsonify({"gpios": list_gpios()})


@app.route("/api/gpio/export", methods=["POST"])
def api_gpio_export():
    body, err, code = _require_json("pin")
    if err:
        return err, code
    pin = body["pin"]
    if not isinstance(pin, int):
        return jsonify({"error": "'pin' must be an integer"}), 400
    ok = export_gpio(pin)
    if not ok:
        return jsonify({"error": "Failed to export GPIO %d" % pin}), 500
    return jsonify({"status": "ok", "pin": pin, "state": get_gpio(pin)})


@app.route("/api/gpio/unexport", methods=["POST"])
def api_gpio_unexport():
    body, err, code = _require_json("pin")
    if err:
        return err, code
    pin = body["pin"]
    if not isinstance(pin, int):
        return jsonify({"error": "'pin' must be an integer"}), 400
    ok = unexport_gpio(pin)
    if not ok:
        return jsonify({"error": "Failed to unexport GPIO %d" % pin}), 500
    return jsonify({"status": "ok", "pin": pin})


@app.route("/api/gpio/<int:pin>", methods=["GET"])
def api_gpio_get(pin):
    return jsonify({"gpio": get_gpio(pin)})


@app.route("/api/gpio/<int:pin>/direction", methods=["POST"])
def api_gpio_direction(pin):
    body, err, code = _require_json("direction")
    if err:
        return err, code
    direction = body["direction"]
    if direction not in ("in", "out"):
        return jsonify({"error": "'direction' must be 'in' or 'out'"}), 400
    ok = set_direction(pin, direction)
    if not ok:
        return jsonify({"error": "Failed to set GPIO %d direction" % pin}), 500
    return jsonify({"status": "ok", "pin": pin, "direction": direction, "state": get_gpio(pin)})


@app.route("/api/gpio/<int:pin>/value", methods=["POST"])
def api_gpio_value(pin):
    body, err, code = _require_json("value")
    if err:
        return err, code
    value = body["value"]
    if value not in (0, 1):
        return jsonify({"error": "'value' must be 0 or 1"}), 400
    ok = set_value(pin, value)
    if not ok:
        return jsonify({"error": "Failed to set GPIO %d value" % pin}), 500
    return jsonify({"status": "ok", "pin": pin, "value": value})


# --- System ---

@app.route("/api/system/restart", methods=["POST"])
def api_system_restart():
    logger.warning("Restart requested via API")
    request_restart()
    threading.Thread(target=_delayed_exit, daemon=True).start()
    return jsonify({"status": "restarting"})


SWAGGER_UI_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TinyTrade AI API</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: "/api/openapi.json", dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis], layout: "BaseLayout" });
  </script>
</body>
</html>"""


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "TinyTrade AI API",
        "version": "1.0.0",
        "description": "Edge Market Intelligence Terminal — manage configs, control displays, read market data, configure GPIO, and restart the service.\n\nRuns on Orange Pi 2G-IOT (256MB RAM) with SSD1306 OLED.",
    },
    "servers": [{"url": "/", "description": "Orange Pi 2G-IOT"}],
    "paths": {
        "/api/status": {
            "get": {
                "summary": "System health",
                "description": "Uptime, memory, OLED/LCD availability, current screen indices.",
                "responses": {
                    "200": {
                        "description": "Status object",
                        "content": {"application/json": {"schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "uptime_seconds": {"type": "integer"},
                                "memory_kb": {"type": "object"},
                                "displays": {"type": "object"},
                            },
                        }}},
                    }
                },
            }
        },
        "/api/prices": {
            "get": {
                "summary": "All asset prices",
                "responses": {"200": {"description": "Array of price objects"}},
            }
        },
        "/api/prices/{symbol}": {
            "get": {
                "summary": "Single asset price",
                "parameters": [
                    {"name": "symbol", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {
                    "200": {"description": "Price object"},
                    "404": {"description": "Symbol not found"},
                },
            }
        },
        "/api/sentiment": {
            "get": {
                "summary": "Recent sentiment results",
                "parameters": [
                    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 10}}
                ],
                "responses": {"200": {"description": "Array of sentiment objects"}},
            }
        },
        "/api/alerts": {
            "get": {
                "summary": "Recent anomaly alerts",
                "parameters": [
                    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 10}}
                ],
                "responses": {"200": {"description": "Array of alert objects"}},
            }
        },
        "/api/config": {
            "get": {
                "summary": "Read runtime config",
                "responses": {"200": {"description": "All config key-value pairs"}},
            },
            "put": {
                "summary": "Update runtime config",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {
                            "crypto_poll_interval": {"type": "integer"},
                            "stocks_poll_interval": {"type": "integer"},
                            "news_poll_interval": {"type": "integer"},
                            "screen_rotation_interval": {"type": "integer"},
                            "oled_enabled": {"type": "boolean"},
                            "lcd_enabled": {"type": "boolean"},
                        },
                    }}},
                },
                "responses": {
                    "200": {"description": "Updated config with previous values"},
                    "400": {"description": "Invalid keys"},
                },
            },
        },
        "/api/display/screen/oled": {
            "post": {
                "summary": "Force OLED to screen index",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {"screen": {"type": "integer"}},
                        "required": ["screen"],
                    }}},
                },
                "responses": {
                    "200": {"description": "Screen set"},
                    "400": {"description": "Invalid index"},
                    "503": {"description": "OLED not available"},
                },
            }
        },
        "/api/display/screen/lcd": {
            "post": {
                "summary": "Force LCD to screen index",
                "requestBody": {
                    "required": True, "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {"screen": {"type": "integer"}},
                        "required": ["screen"],
                    }}},
                },
                "responses": {
                    "200": {"description": "Screen set"},
                    "400": {"description": "Invalid index"},
                    "503": {"description": "LCD not available"},
                },
            }
        },
        "/api/display/oled/test": {
            "post": {
                "summary": "Show OLED test pattern",
                "responses": {
                    "200": {"description": "Pattern displayed"},
                    "500": {"description": "OLED error"},
                },
            }
        },
        "/api/display/oled/clear": {
            "post": {
                "summary": "Clear OLED screen",
                "responses": {
                    "200": {"description": "OLED cleared"},
                    "500": {"description": "OLED error"},
                },
            }
        },
        "/api/display/oled/reset": {
            "post": {
                "summary": "Reset and re-initialize OLED",
                "responses": {
                    "200": {"description": "OLED reset (may return degraded status)"},
                },
            }
        },
        "/api/display/lcd/test": {
            "post": {
                "summary": "Show LCD test pattern",
                "responses": {
                    "200": {"description": "Pattern displayed"},
                    "500": {"description": "LCD not available"},
                },
            }
        },
        "/api/display/lcd/clear": {
            "post": {
                "summary": "Clear LCD screen",
                "responses": {
                    "200": {"description": "LCD cleared"},
                    "500": {"description": "LCD not available"},
                },
            }
        },
        "/api/display/lcd/reset": {
            "post": {
                "summary": "Reset and re-initialize LCD",
                "responses": {
                    "200": {"description": "LCD reset (may return degraded status)"},
                },
            }
        },
        "/api/gpio": {
            "get": {
                "summary": "List all known GPIOs",
                "responses": {"200": {"description": "Array of GPIO pin states"}},
            }
        },
        "/api/gpio/export": {
            "post": {
                "summary": "Export a GPIO pin",
                "requestBody": {
                    "required": True, "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {"pin": {"type": "integer"}},
                        "required": ["pin"],
                    }}},
                },
                "responses": {"200": {"description": "GPIO exported"}},
            }
        },
        "/api/gpio/unexport": {
            "post": {
                "summary": "Unexport a GPIO pin",
                "requestBody": {
                    "required": True, "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {"pin": {"type": "integer"}},
                        "required": ["pin"],
                    }}},
                },
                "responses": {"200": {"description": "GPIO unexported"}},
            }
        },
        "/api/gpio/{pin}": {
            "get": {
                "summary": "Get single GPIO state",
                "parameters": [
                    {"name": "pin", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {"200": {"description": "GPIO state object"}},
            }
        },
        "/api/gpio/{pin}/direction": {
            "post": {
                "summary": "Set GPIO direction",
                "parameters": [
                    {"name": "pin", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "requestBody": {
                    "required": True, "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {"direction": {"type": "string", "enum": ["in", "out"]}},
                        "required": ["direction"],
                    }}},
                },
                "responses": {"200": {"description": "Direction set"}},
            }
        },
        "/api/gpio/{pin}/value": {
            "post": {
                "summary": "Set GPIO output value",
                "parameters": [
                    {"name": "pin", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "requestBody": {
                    "required": True, "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {"value": {"type": "integer", "enum": [0, 1]}},
                        "required": ["value"],
                    }}},
                },
                "responses": {"200": {"description": "Value set"}},
            }
        },
        "/api/system/restart": {
            "post": {
                "summary": "Restart the application",
                "description": "Graceful shutdown. Systemd Restart=always respawns the service.",
                "responses": {"200": {"description": "Restart initiated"}},
            }
        },
    },
}


@app.route("/api/openapi.json")
def api_openapi():
    return jsonify(OPENAPI_SPEC)


@app.route("/api/docs")
def api_docs():
    return render_template_string(SWAGGER_UI_HTML)


def start_api(host="0.0.0.0", port=5000):
    logger.info("Starting API on %s:%d", host, port)
    app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)
