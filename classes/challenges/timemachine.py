"""Contains functions for running a no time machine challenge."""
import time

from classes.features   import Adventure, Augmentation, BloodMagic
from classes.features   import MoneyPit, Wandoos, FightBoss
from classes.misc       import Misc, Rebirth
from classes.processing import Processing

import coordinates as coords


buster_assigned = False
final_aug = False

def first_rebirth(duration):
    """Procedure for first rebirth."""
    global buster_assigned, final_aug

    ss_assigned = False
    adventure_pushed = False

    FightBoss.nuke()
    Adventure.set_zone()
    while Processing.check_pixel_color(*coords.COLOR_TM_LOCKED):
        if not ss_assigned:
            time.sleep(1)
            Augmentation.assign_energy({"SS": 1}, Misc.get_idle_cap(1))
            ss_assigned = True
        Wandoos.cap_dumps(True, True)
        if Wandoos.get_bb_status():
            Augmentation.assign_energy({"SS": 1}, Misc.get_idle_cap(1))
        FightBoss.nuke()
        time.sleep(2)
        FightBoss.fight()
    if ss_assigned:
        Misc.reclaim_aug()
    Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))

    while Processing.check_pixel_color(*coords.COLOR_BM_LOCKED):
        Wandoos.cap_dumps(True, True)
        if Wandoos.get_bb_status():
            Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
        FightBoss.nuke()
        FightBoss.fight()
    BloodMagic.toggle_auto_spells(drop=False, gold=False)
    BloodMagic.blood_magic(8)
    rb_time = Rebirth.time_()
    while int(rb_time.timestamp.tm_min) < duration:
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        time.sleep(2)
        try:
            current_boss = int(FightBoss.get_current_boss())
            if current_boss > 28 and current_boss < 49:
                if not buster_assigned:
                    Misc.reclaim_aug()
                    buster_assigned = True
                Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))

            elif current_boss >= 49:
                if not final_aug:
                    Misc.reclaim_aug()
                    final_aug = True
                    time.sleep(1)
                Augmentation.assign_energy({"EB": 0.66, "CS": 0.34}, Misc.get_idle_cap(1))
            if current_boss > 58 and not adventure_pushed:
                Adventure.set_zone()
                adventure_pushed = True
        except ValueError:
            print("couldn't get current boss")
        rb_time = Rebirth.time_()

def speedrun(duration):
    """Start a speedrun.

    Keyword arguments
    duration -- duration in minutes to run
    f -- feature object
    """
    global buster_assigned, final_aug
   
    Rebirth.rebirth()
    FightBoss.nuke()
    time.sleep(2)
    Adventure.set_zone()

    try:
        current_boss = int(FightBoss.get_current_boss())
        if current_boss > 28 and current_boss < 49:
            Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
        elif current_boss >= 49:
            Augmentation.assign_energy({"EB": 0.66, "CS": 0.34}, Misc.get_idle_cap(1))
    except ValueError:
        print("couldn't get current boss")

    while Processing.check_pixel_color(*coords.COLOR_TM_LOCKED):
        FightBoss.nuke()
        FightBoss.fight()
        Wandoos.cap_dumps(True, True)

    while Processing.check_pixel_color(*coords.COLOR_BM_LOCKED):
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        time.sleep(2)
        FightBoss.fight()

    BloodMagic.blood_magic(8)
    Wandoos.cap_dumps(True, True)
    rb_time = Rebirth.time_()
    while int(rb_time.timestamp.tm_min) < duration:
        FightBoss.nuke()
        FightBoss.fight()
        Adventure.set_zone()
        Wandoos.cap_dumps(True, True)
        if Wandoos.get_bb_status():
            Augmentation.assign_energy({"EB": 0.66, "CS": 0.34}, Misc.get_idle_cap(1))
        # If current rebirth is scheduled for more than 3 minutes and
        # we already finished the rebirth, we will return here, instead
        # of waiting for the duration. Since we cannot start a new
        # challenge if less than 3 minutes have passed, we must always
        # wait at least 3 minutes.
        rb_time = Rebirth.time_()
        if duration > 3:
            if not Rebirth.check_challenge():
                while int(rb_time.timestamp.tm_min) < 3:
                    rb_time = Rebirth.time_()
                    time.sleep(1)
                MoneyPit.pit()
                MoneyPit.spin()
                return

    MoneyPit.pit()
    MoneyPit.spin()
    return

def timemachine():
    """Run no time machine challenge."""
    Wandoos.set_wandoos(0)
    first_rebirth(3)
    if not Rebirth.check_challenge():
        return
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
    return
