"""Contains functions for running a basic challenge."""
import time

from classes.features   import AdvancedTraining, Adventure, Augmentation
from classes.features   import BloodMagic, FightBoss, GoldDiggers
from classes.features   import TimeMachine, Wandoos
from classes.misc       import Misc, Rebirth
from classes.processing import Processing

import coordinates as coords


current_boss = 1
minutes_elapsed = 0
advanced_training_locked = True
bm_locked = True
tm_locked = True

def speedrun(duration, *, blood=False, adv=False):
    """Start a speedrun.

    Keyword arguments
    duration -- duration in minutes to run
    f -- feature object
    """
    global current_boss, minutes_elapsed, advanced_training_locked, bm_locked, tm_locked

    print(f"Current boss: {current_boss}")

    current_boss = 1
    minutes_elapsed = 0
    advanced_training_locked = True
    bm_locked = True
    tm_locked = True

    diggers = [2, 3, 11, 12]
    adv_training_assigned = False

    Rebirth.rebirth()
    Wandoos.cap_dumps(True, True)
    FightBoss.nuke()
    time.sleep(2)
    FightBoss.fight()
    Adventure.set_zone()
    update_gamestate()

    while current_boss < 18 and minutes_elapsed < duration:  # augs unlocks after 17
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        if not advanced_training_locked and not adv_training_assigned:
            if adv: print("assigning adv")
            AdvancedTraining.assign_energy(4e11)
            adv_training_assigned = True
        update_gamestate()
    Adventure.set_zone()

    while current_boss < 29 and minutes_elapsed < duration:  # buster unlocks after 28
        Augmentation.assign_energy({"SS": 1}, Misc.get_idle_cap(1))
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        if not advanced_training_locked and not adv_training_assigned:
            if adv: print("assigning adv")
            Misc.reclaim_aug()
            AdvancedTraining.assign_energy(4e11)
            Augmentation.assign_energy({"SS": 1}, Misc.get_idle_cap(1))
            adv_training_assigned = True
        update_gamestate()

    if minutes_elapsed < duration:  # only reclaim if we're not out of time
        Misc.reclaim_aug()

    while current_boss < 31 and minutes_elapsed < duration:  # TM unlocks after 31
        Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        if not advanced_training_locked and not adv_training_assigned:
            if adv: print("assigning adv")
            Misc.reclaim_aug()
            AdvancedTraining.assign_energy(4e11)
            Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
            adv_training_assigned = True
        update_gamestate()

    if minutes_elapsed < duration:  # only reclaim if we're not out of time
        Misc.reclaim_aug()  # get some energy back for TM
        Misc.reclaim_res(magic=True)  # get all magic back from wandoos
        TimeMachine.assign_resources(Misc.get_idle_cap(1) * 0.05, m=Misc.get_idle_cap(2) * 0.05)

    while current_boss < 38 and minutes_elapsed < duration:  # BM unlocks after 37
        GoldDiggers.activate(diggers)
        Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        if not advanced_training_locked and not adv_training_assigned:
            if adv: print("assigning adv")
            Misc.reclaim_aug()
            AdvancedTraining.assign_energy(4e11)
            Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
            adv_training_assigned = True
        update_gamestate()

    if minutes_elapsed < duration:
        BloodMagic.blood_magic(8)
        BloodMagic.toggle_auto_spells(drop=False)
        time.sleep(10)
        if blood: print("waiting 10 seconds for gold ritual")
        BloodMagic.toggle_auto_spells(drop=False, gold=False)

    while current_boss < 49 and minutes_elapsed < duration:
        GoldDiggers.activate(diggers)
        Wandoos.cap_dumps(True, True)
        Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
        FightBoss.nuke()
        FightBoss.fight()
        if not advanced_training_locked and not adv_training_assigned:
            if adv: print("assigning adv")
            Misc.reclaim_aug()
            AdvancedTraining.assign_energy(4e11)
            Augmentation.assign_energy({"EB": 1}, Misc.get_idle_cap(1))
            adv_training_assigned = True
        update_gamestate()
    if minutes_elapsed < duration:  # only reclaim if we're not out of time
        Misc.reclaim_aug()

    while minutes_elapsed < duration:
        Augmentation.assign_energy({"AE": 0.8, "ES": 0.2}, Misc.get_idle_cap(1))
        GoldDiggers.activate(diggers)
        Wandoos.cap_dumps(True, True)
        FightBoss.nuke()
        FightBoss.fight()
        if not advanced_training_locked and not adv_training_assigned:
            if adv: print("assigning adv")
            Misc.reclaim_aug()
            AdvancedTraining.assign_energy(4e11)
            Augmentation.assign_energy({"AE": 0.8, "ES": 0.2}, Misc.get_idle_cap(1))
            adv_training_assigned = True
        update_gamestate()
        if not Rebirth.check_challenge() and minutes_elapsed >= 3:
            return
 
    return

def update_gamestate():
    """Update relevant state information."""
    global current_boss, minutes_elapsed, advanced_training_locked, bm_locked, tm_locked

    rb_time = Rebirth.time_()
    minutes_elapsed = int(rb_time.timestamp.tm_min)
    try:
        current_boss = int(FightBoss.get_current_boss())
    except ValueError:
        current_boss = 1
        print("couldn't get current boss")

    if advanced_training_locked:
        advanced_training_locked = Processing.check_pixel_color(*coords.COLOR_ADV_TRAINING_LOCKED)
    if bm_locked:
        bm_locked = Processing.check_pixel_color(*coords.COLOR_BM_LOCKED)
    if tm_locked:
        tm_locked = Processing.check_pixel_color(*coords.COLOR_TM_LOCKED)
    
def basic(*, guff :bool =False):
    """Run basic challenge."""
    global current_boss

    try:
        current_boss = int(FightBoss.get_current_boss())
    except ValueError:
        current_boss = 1
        print("couldn't get current boss")

    if not guff:
        Wandoos.set_wandoos(2)
        for _ in range(2):
            speedrun(3)
            if not Rebirth.check_challenge():
                return
        for _ in range(3):
            speedrun(7)
            if not Rebirth.check_challenge():
                return
        for _ in range(4):
            speedrun(12)
            if not Rebirth.check_challenge():
                return

    for _ in range(4):
        speedrun(30)
        if not Rebirth.check_challenge():
            return
    while True:
        speedrun(60)
        if not Rebirth.check_challenge():
            return
    return
