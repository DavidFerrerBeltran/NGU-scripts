"""Contains functions for running a blind challenge."""
import time

import coordinates as coords

from classes.features   import Adventure, Augmentation, BloodMagic, FightBoss
from classes.features   import GoldDiggers, TimeMachine, Wandoos
from classes.misc       import Rebirth
from classes.processing import Processing

advanced_training_locked = True
bm_locked = True
tm_locked = True

def run(duration):
    """Procedure for Blind Challenge RBs."""
    global advanced_training_locked, bm_locked, tm_locked

    advanced_training_locked = True
    bm_locked = True
    tm_locked = True

    tm_assigned = False
    bm_assigned = False

    end = time.time() + duration * 60 + 10
    FightBoss.nuke()
    time.sleep(2)
    FightBoss.fight()
    diggers = [2, 3, 11, 12]
    Adventure.set_zone(0)
    Augmentation.assign_energy({"SS": 1}, 1e12)
    GoldDiggers.activate(diggers)
    while time.time() < end:
        Augmentation.assign_energy({"EB": 0.66, "CS": 0.34}, 1e13)
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        GoldDiggers.activate(diggers)
        update_gamestate()
        if not tm_locked and not tm_assigned:
            TimeMachine.assign_resources(1e13, m=1e13)
            tm_assigned = True
        if not bm_locked and not bm_assigned:
            BloodMagic.blood_magic(8)
            bm_assigned = True
        if not Rebirth.check_challenge() and end - time.time() > 180:
            return
    if not Rebirth.check_challenge():
        return
    Rebirth.rebirth()
    return

def update_gamestate():
    """Update relevant state information."""
    global advanced_training_locked, bm_locked, tm_locked

    if advanced_training_locked:
        advanced_training_locked = Processing.check_pixel_color(*coords.COLOR_ADV_TRAINING_LOCKED)
    if bm_locked:
        bm_locked = Processing.check_pixel_color(*coords.COLOR_BM_LOCKED)
    if tm_locked:
        tm_locked = Processing.check_pixel_color(*coords.COLOR_TM_LOCKED)

def blind():
    """Run blind challenge."""
    for _ in range(8):
        run(3)
        if not Rebirth.check_challenge():
            return
    for _ in range(5):
        run(7)
        if not Rebirth.check_challenge():
            return
    for _ in range(5):
        run(12)
        if not Rebirth.check_challenge():
            return
    for _ in range(5):
        run(60)
        if not Rebirth.check_challenge():
            return
