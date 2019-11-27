"""Contains functions for running a no equipment challenge."""
import time

import coordinates as coords

from classes.features   import Adventure, Augmentation, BloodMagic, FightBoss
from classes.features   import GoldDiggers, MoneyPit, Wandoos
from classes.misc       import Rebirth
from classes.processing import Processing


def speedrun(duration):
    """Start a speedrun.

    Keyword arguments
    duration -- duration in minutes to run
    f -- feature object
    """
    diggers = [2, 3, 11, 12]
    FightBoss.nuke()
    time.sleep(2)

    FightBoss.fight()
    Adventure.set_zone()
    time.sleep(2)

    rb_time = Rebirth.time_()
    while int(rb_time.timestamp.tm_min) < duration:
        GoldDiggers.activate(diggers)
        Wandoos.cap_dumps(True, True)
        Augmentation.assign_energy({"SM": 1}, coords.INPUT_MAX)
        if not Processing.check_pixel_color(*coords.COLOR_TM_LOCKED):
            BloodMagic.blood_magic(6)
        FightBoss.nuke()
        rb_time = Rebirth.time_()
    MoneyPit.pit()
    MoneyPit.spin()
    return

def equipment():
    """Run no equipment challenge."""
    Wandoos.set_wandoos(0)  # wandoos 98, use 1 for meh

    for _ in range(8):
        speedrun(3)
        if not Rebirth.check_challenge():
            return
        Rebirth.rebirth()
    for _ in range(5):
        speedrun(7)
        if not Rebirth.check_challenge():
            return
        Rebirth.rebirth()
    for _ in range(5):
        speedrun(12)
        if not Rebirth.check_challenge():
            return
        Rebirth.rebirth()
    for _ in range(5):
        speedrun(60)
        if not Rebirth.check_challenge():
            return
        Rebirth.rebirth()
    return
