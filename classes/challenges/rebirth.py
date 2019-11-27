"""Contains functions for running a no rebirth challenge."""
import time

from classes.features   import FightBoss, GoldDiggers, Adventure, Augmentation
from classes.features   import BloodMagic, Wandoos, TimeMachine
from classes.misc       import Misc, Rebirth
from classes.processing import Processing

import coordinates  as coords


def first_rebirth():
    """Procedure for first rebirth."""
    final_aug   = False
    ss_assigned = False

    end = time.time() + 3 * 60

    FightBoss.nuke()
    time.sleep(2)

    FightBoss.fight()
    Adventure.set_zone()
    while Processing.check_pixel_color(*coords.COLOR_TM_LOCKED):
        if not ss_assigned:
            time.sleep(1)
            Augmentation.assign_energy({"SS": 1}, 3e12)
            ss_assigned = True
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        time.sleep(2)
        FightBoss.fight()

    TimeMachine.assign_resources(1e9, magic=True)
    Augmentation.assign_energy({"DS": 1}, 1e12)
    GoldDiggers.activate()
    Adventure.itopod()

    while Processing.check_pixel_color(*coords.COLOR_BM_LOCKED) or Processing.check_pixel_color(*coords.COLOR_BM_LOCKED_ALT):
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        time.sleep(2)
        FightBoss.fight()
        GoldDiggers.activate()
    BloodMagic.blood_magic(8)
    BloodMagic.toggle_auto_spells(drop=False, number=False)
    while time.time() < end - 90:
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        time.sleep(2)
        try:
            current_boss = int(FightBoss.get_current_boss())
            if current_boss > 36:
                Augmentation.assign_energy({"SS": 0.67, "DS": 0.33}, Misc.get_idle_cap(1))
        except ValueError:
            print("couldn't get current boss")
        GoldDiggers.activate()

    while True:
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        time.sleep(1)
        try:
            current_boss = int(FightBoss.get_current_boss())
            if current_boss > 45:
                if not final_aug:
                    Misc.reclaim_aug()
                    final_aug = True
                Augmentation.assign_energy({"SM": 0.67, "AA": 0.33}, Misc.get_idle_cap(1))
        except ValueError:
            print("couldn't get current boss")
        FightBoss.fight()
        GoldDiggers.activate()

        if time.time() > end and not Rebirth.check_challenge():
            return

def rebirth():
    """Run no rebirth challenge."""
    first_rebirth()
