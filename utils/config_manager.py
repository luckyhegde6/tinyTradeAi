import json, os, threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME_CONFIG_PATH = os.path.join(BASE_DIR, "runtime_config.json")

_lock = threading.RLock()

DEFAULTS = {
    "crypto_poll_interval": 60,
    "stocks_poll_interval": 900,
    "news_poll_interval": 900,
    "screen_rotation_interval": 5,
    "oled_enabled": True,
    "lcd_enabled": False,
}

_config = None


def load():
    global _config
    if _config is not None:
        return _config
    with _lock:
        try:
            with open(RUNTIME_CONFIG_PATH) as f:
                _config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _config = DEFAULTS.copy()
            save()
    return _config


def save():
    with _lock:
        with open(RUNTIME_CONFIG_PATH, "w") as f:
            json.dump(_config, f, indent=2)


def get_all():
    load()
    return dict(_config)


def get(key, default=None):
    load()
    return _config.get(key, default)


def set(key, value):
    load()
    with _lock:
        old = _config.get(key)
        _config[key] = value
        save()
    return old


def set_many(updates):
    load()
    with _lock:
        old = {k: _config.get(k) for k in updates}
        _config.update(updates)
        save()
    return old
