"""ITOPOD Sniping script."""
import argparse
import time
# Helper classes
from classes.features import Adventure, GoldDiggers, MoneyPit, Inventory
from classes.helper   import Helper
from classes.stats    import Tracker

import constants as const

parser = argparse.ArgumentParser()
parser.add_argument(
    "-u", "--untrack", action='store_true',
    help="set this flag run without EXP/PP tracker")
args = parser.parse_args()

Helper.init(True)
Helper.requirements()

if not args.untrack: tracker = Tracker(5)
Adventure.itopod(blue=False, lazy=True)

while True:  # main loop
    titans = Adventure.get_titan_status()
    if titans:
        for titan in titans:
            Adventure.kill_titan(titan)
    Adventure.set_idle(False)
    Adventure.snipe(300, regular=True)
    MoneyPit.pit()
    if not args.untrack: tracker.progress()
    GoldDiggers.activate(const.DEFAULT_DIGGER_ORDER)
    Inventory.boost_equipment(boost_cube=True)
    time.sleep(3)  # Need to wait for tooltip to disappear
