"""Snipe without Mega Buff."""
import time

# Helper classes
from classes.features   import Adventure, MoneyPit
from classes.helper     import Helper

Helper.init(True)

while True:  # main loop    
    Adventure.snipe(0, 10, manual=True, bosses=True, highest=True)
    Adventure.adventure(0)  # go wait at safe zone
    
    MoneyPit.pit()
    MoneyPit.spin()

    time.sleep(10)
