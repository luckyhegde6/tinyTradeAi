import sys, os, time
sys.path.insert(0, '/opt/tinyTradeAi')
os.environ['FLASK_ENV'] = 'testing'

from database.db import init_db
init_db()

import utils.helpers as helpers
helpers.is_nse_market_open = lambda: True
helpers.is_us_market_open = lambda: True

import oled.animations as anim

anim._last_build_time = -1
anim.build_screens()

print("Testing %d screens..." % len(anim.SCREENS))
for i, s in enumerate(anim.SCREENS):
    name = s.__name__
    try:
        img = s()
        print("  [%d/%d] %s - %dx%d OK" % (i+1, len(anim.SCREENS), name, img.width, img.height))
    except Exception as ex:
        print("  [%d/%d] %s - FAIL: %s" % (i+1, len(anim.SCREENS), name, ex))

from oled.display import get_oled_device
dev = get_oled_device()
if dev:
    print("\nRendering on OLED (3s each)...")
    for i, s in enumerate(anim.SCREENS):
        try:
            img = s()
            dev.display(img)
            print("  [%d/%d] %s" % (i+1, len(anim.SCREENS), s.__name__))
            time.sleep(3)
        except Exception as ex:
            print("  [%d/%d] %s - FAIL: %s" % (i+1, len(anim.SCREENS), s.__name__, ex))
    print("\nScreen cycle complete.")
else:
    print("\nNo OLED device available.")
    print("Screen functions verified - OLED render skipped (no hardware).")
