"""Snipe with Mega Buff."""
import argparse

# Helper classes
from classes.features   import Adventure, GoldDiggers, MoneyPit, Inventory, Yggdrasil
from classes.helper     import Helper
from classes.processing import Processing

import coordinates  as coords

Helper.init(True)
Helper.requirements()

parser = argparse.ArgumentParser()
parser.add_argument("-z", "--zone", required=True, type=int, help="select which zone you wish to snipe")
args = parser.parse_args()

Adventure.set_zone(1)
Adventure.set_idle(False)

while True:  # main loop
    GoldDiggers.activate([4, 1])
    
    while not Processing.check_pixel_color(*coords.COLOR_MEGA_BUFF_READY):
        Adventure.itopod()  # go wait at ITOPOD
        Adventure.snipe(regular=True)

    Adventure.set_zone(args.zone)
    Adventure.snipe()

    MoneyPit.pit()
    MoneyPit.spin()
    Yggdrasil.harvest()
    Inventory.merge_equipment()
    Inventory.boost_equipment()
    