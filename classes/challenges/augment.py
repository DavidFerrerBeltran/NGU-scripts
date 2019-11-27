"""Contains functions for running a no augments challenge."""
import time

from classes.features   import Adventure, BloodMagic, FightBoss
from classes.features   import TimeMachine, Wandoos, GoldDiggers
from classes.misc       import Misc, Rebirth
from classes.processing import Processing

import coordinates as coords


def normal_rebirth(duration):
    """Procedure for first rebirth."""
    diggers = [2, 3, 11, 12]  # Wandoos, stat, blood, exp
    FightBoss.nuke()
    time.sleep(2)
    FightBoss.fight()
    Adventure.set_zone(0)
    Wandoos.set_wandoos(1)  # wandoos Meh, use 0 for 98
    BloodMagic.toggle_auto_spells(drop=False)
    GoldDiggers.activate(diggers)
    while Processing.check_pixel_color(*coords.COLOR_TM_LOCKED):
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        time.sleep(2)
        FightBoss.fight()

    TimeMachine.assign_resources(Misc.get_idle_cap(1) * 0.1, magic=True)
    Adventure.itopod()

    while Processing.check_pixel_color(*coords.COLOR_BM_LOCKED):
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        time.sleep(2)
        FightBoss.fight()
        GoldDiggers.activate(diggers)
    BloodMagic.blood_magic(8)
    rb_time = Rebirth.time_()
    while int(rb_time.timestamp.tm_min) < duration:
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        time.sleep(2)
        GoldDiggers.activate(diggers)
        rb_time = Rebirth.time_()
        # return if challenge is completed and rebirth time is above 3 minutes
        if int(rb_time.timestamp.tm_min) >= 3 and not Rebirth.check_challenge():
            return

    Rebirth.rebirth()
    
def augment():
    """Run no augments challenge."""
    for _ in range(8):  # runs 3-minute rebirth 8 times, if we still aren't done move to 7 min
        normal_rebirth(3)  # start a run with a 3 minute duration
        if not Rebirth.check_challenge(): return
    for _ in range(5):
        normal_rebirth(7)
        if not Rebirth.check_challenge(): return
    for _ in range(5):
        normal_rebirth(12)
        if not Rebirth.check_challenge(): return
    for _ in range(5):
        normal_rebirth(60)
        if not Rebirth.check_challenge(): return
    return
