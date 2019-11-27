"""24-hour rebirth script."""
import time

from classes.features   import AdvancedTraining, Adventure, Augmentation, FightBoss
from classes.features   import BloodMagic, GoldDiggers, NGU, Wandoos, TimeMachine
from classes.features   import Questing, Yggdrasil, Inventory, MoneyPit
from classes.misc       import Misc, Rebirth
from classes.helper     import Helper

# Set these to your own loadouts
# Set them to zero to disable
AT_loadout = 2
PP_loadout = 1
gold_loadout = 0
NGU_loadout = 5
Ygg_loadout = 4

def finish_and_rebirth():
    pass

#####

# Set these to your own loadouts
respawn_loadout = 1
ygg_loadout = 2

Helper.init()
Helper.requirements()


def rebirth_init(rt):
    """Procedure that handles start of rebirth."""
    Misc.reclaim_all()  # make sure we reset e/m if we run this mid-rebirth
    FightBoss.nuke(101)  # PPP
    Inventory.loadout(respawn_loadout)
    Adventure.set_zone(0)
    TimeMachine.assign_resources(5e11, magic=True)
    Augmentation.assign_energy({"CI": 0.7, "ML": 0.3}, 1e12)
    BloodMagic.blood_magic(8)
    BloodMagic.toggle_auto_spells()
    GoldDiggers.activate()

    if rt.timestamp.tm_hour > 0 or rt.timestamp.tm_min >= 13:
        print("assigning adv training")
    else:
        duration = (12.5 - rt.timestamp.tm_min) * 60
        print(f"doing itopod for {duration} seconds while waiting for adv training to activate")
        Adventure.old_itopod_snipe(duration)

    AdvancedTraining.assign_energy(2e12)
    GoldDiggers.activate()
    Misc.reclaim_bm()
    Wandoos.cap_dumps(True)
    NGU.assign(Misc.get_idle_cap(2), range(1, 9), False)
    NGU.assign(Misc.get_idle_cap(1), range(1, 7), True)

rbtime = Rebirth.time_()
rebirth_init(rbtime)

while True:
    rbtime = Rebirth.time_()
    FightBoss.nuke()
    GoldDiggers.activate()
    Inventory.merge_inventory(8)  # merge uneqipped guffs
    spells = BloodMagic.get_spells_ready()
    if spells:  # check if any spells are off CD
        Misc.reclaim_ngu(True)  # take all magic from magic NGUs
        for spell in spells:
            BloodMagic.cast_spell(spell)
        Misc.reclaim_bm()
        NGU.assign(Misc.get_idle_cap(1), range(1, 7), True)
        BloodMagic.toggle_auto_spells()  # retoggle autospells

    if rbtime.days > 0:  # rebirth is at >24 hours
        print(f"rebirthing at {rbtime}")  # debug
        FightBoss.nuke()
        MoneyPit.spin()
        GoldDiggers.deactivate_all()
        Yggdrasil.harvest(equip=1)  # harvest with equipment set 1
        Yggdrasil.harvest(eat_all=True)
        GoldDiggers.level_all()  # level all diggers
        Rebirth.rebirth()
        time.sleep(3)
        rbtime = Rebirth.time_()
        rebirth_init(rbtime)
    else:
        Yggdrasil.harvest()
        Misc.save_check()
        MoneyPit.pit()
        if rbtime.timestamp.tm_hour <= 12:  # quests for first 12 hours
            titans = Adventure.get_titan_status()
            if titans:
                for titan in titans:
                    Adventure.kill_titan(titan)
            Inventory.boost_cube()
            Questing.questing()
            time.sleep(3)
        else:  # after hour 12, do itopod in 5-minute intervals
            titans = Adventure.get_titan_status()
            if titans:
                for titan in titans:
                    Adventure.kill_titan(titan)
            Adventure.old_itopod_snipe(300)
            Inventory.boost_cube()
