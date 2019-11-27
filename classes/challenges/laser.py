"""Contains functions for running a laser sword challenge."""
import time

from classes.features import FightBoss, Wandoos, Adventure, TimeMachine
from classes.features import GoldDiggers, BloodMagic, Augmentation
from classes.misc     import Misc, Rebirth


def speedrun():
    """Start a speedrun.

    Keyword arguments
    duration -- duration in minutes to run
    f -- feature object
    """
    diggers = [2, 3, 11, 12]
    FightBoss.nuke()
    Wandoos.set_wandoos(0)
    Adventure.set_zone()
    TimeMachine.assign_resources(Misc.get_idle_cap(1) * 0.01, magic=True)
    GoldDiggers.activate(diggers)
    Wandoos.cap_dumps(True, True)
    BloodMagic.blood_magic(8)
    while Rebirth.check_challenge():
        FightBoss.nuke()
        Augmentation.assign_energy({"LS": 0.92, "QSL": 0.08}, Misc.get_idle_cap(1))
        GoldDiggers.activate(diggers)

    rb_time = Rebirth.time_()
    while int(rb_time.timestamp.tm_min) < 3:
        rb_time = Rebirth.time_()
        time.sleep(1)

def laser():
    """Run laser sword challenge."""
    speedrun()
