"""Contains functions for running a 100 level challenge."""
import time

from classes.features import FightBoss, Adventure, Augmentation, GoldDiggers
from classes.misc     import Misc, Rebirth

import coordinates as coords


def speedrun(duration):
    """Procedure for first rebirth in a 100LC."""
    FightBoss.nuke()
    time.sleep(2)
    FightBoss.fight()
    diggers = [2, 3, 11, 12]
    Adventure.set_zone()
    current_boss = int(FightBoss.get_current_boss())
    if current_boss > 48:
        Augmentation.assign_energy({"EB": 0.66, "CS": 0.34}, Misc.get_idle_cap(1))
    else:
        Augmentation.assign_energy({"EB": 1}, coords.INPUT_MAX)
    GoldDiggers.activate(diggers)
    rb_time = Rebirth.time_()
    while int(rb_time.timestamp.tm_min) < duration:
        Augmentation.assign_energy({"EB": 0.66, "CS": 0.34}, Misc.get_idle_cap(1))
        FightBoss.nuke()
        FightBoss.fight()
        GoldDiggers.activate(diggers)
        rb_time = Rebirth.time_()
    if not Rebirth.check_challenge() and rb_time.timestamp.tm_min >= 3:
        return
    Rebirth.rebirth()
    return

def level():
    """Run 100 level challenge."""
    for _ in range(8):
        speedrun(3)
        if not Rebirth.check_challenge():
            return
    for _ in range(5):
        speedrun(7)
        if not Rebirth.check_challenge():
            return
    for _ in range(5):
        speedrun(12)
        if not Rebirth.check_challenge():
            return
    for _ in range(5):
        speedrun(60)
        if not Rebirth.check_challenge():
            return
