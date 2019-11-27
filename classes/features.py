"""Feature classes handle the different features in the game."""
from __future__ import annotations

import datetime
import math
import re
import time

from collections        import deque, namedtuple
from typing             import Dict, List, Tuple

from deprecated         import deprecated

import constants        as const
import coordinates      as coords
import usersettings     as userset

from classes.color      import Color
from classes.inputs     import Inputs
from classes.misc       import Misc
from classes.navigation import Navigation
from classes.processing import Processing
from classes.window     import Window


class BasicTraining:
    """This class assumes Sync Trainings is OFF"""
    
    class Const:
        plus_X = 840
        minus_X = 875
        cap_X = 910

        att_Y0 = 140
        def_Y0 = 385

        Y_offset = 35

    @staticmethod
    def precap_att() -> None:
        """Sets up energy to cap all Att trainings even before unlocking them."""
        Navigation.menu("basictraining")
        Inputs.click(BasicTraining.Const.plus_X, BasicTraining.Const.att_Y0, Inputs.Const.MOUSE_RIGHT)
    
    @staticmethod
    def precap_def() -> None:
        """Sets up energy to cap all Def trainings even before unlocking them."""
        Navigation.menu("basictraining")
        Inputs.click(BasicTraining.Const.plus_X, BasicTraining.Const.def_Y0, Inputs.Const.MOUSE_RIGHT)
    
    @staticmethod
    def cap_att(num :int =6) -> None:
        """Caps Att trainings.

        Args:
            num: Cap all Att trainings from 1st to num.
        """
        Navigation.menu("basictraining")
        for x in range(0, num):
            Inputs.click(BasicTraining.Const.cap_X, BasicTraining.Const.att_Y0 + x*BasicTraining.Const.Y_offset, Inputs.Const.MOUSE_LEFT)

    @staticmethod
    def cap_def(num :int =6) -> None:
        """Caps Def trainings.

        Args:
            num: Cap all Def trainings from 1st to num.
        """
        Navigation.menu("basictraining")
        for x in range(0, num):
            Inputs.click(BasicTraining.Const.cap_X, BasicTraining.Const.def_Y0 + x*BasicTraining.Const.Y_offset, Inputs.Const.MOUSE_LEFT)

    @staticmethod
    def reclaim_basics() -> None:
        """Recovers all Energy from Basic Trainings.
        For those who do not know what the Cooking stat serves for.
        """
        for x in range(0, 6):
            Inputs.click(BasicTraining.Const.minus_X, BasicTraining.Const.att_Y0 + x*BasicTraining.Const.Y_offset, Inputs.Const.MOUSE_LEFT)
            Inputs.click(BasicTraining.Const.minus_X, BasicTraining.Const.def_Y0 + x*BasicTraining.Const.Y_offset, Inputs.Const.MOUSE_LEFT)

class FightBoss:
    @staticmethod
    def get_current_boss() -> int:
        """Go to fight and read current boss number."""
        Navigation.menu("fight")
        boss = Processing.ocr(*coords.OCR_BOSS, debug=False)
        return int(Processing.remove_letters(boss))

    @staticmethod
    def nuke(boss :int =None) -> None:
        """Navigate to Fight Boss and Nuke or Fast Fight.

        Args:
	        boss: If provided, will fight until reached
                If omitted, will hit nuke instead.
        """
        Navigation.menu("fight")
        if boss:
            for _ in range(boss):
                Inputs.click(*coords.FIGHT, fast=True)
            time.sleep(userset.SHORT_SLEEP)
            try:
                current_boss = int(FightBoss.get_current_boss())
            except ValueError:
                current_boss = 1
            x = 0
            while current_boss < boss:
                bossdiff = boss - current_boss
                for _ in range(0, bossdiff):
                    Inputs.click(*coords.FIGHT, fast=True)
                time.sleep(userset.SHORT_SLEEP)
                try:
                    current_boss = int(FightBoss.get_current_boss())
                except ValueError:
                    current_boss = 1
                x += 1
                if x > 7:  # Safeguard if number is too low to reach target boss, otherwise we get stuck here
                    print("Couldn't reach the target boss, something probably went wrong the last rebirth.")
                    break
        else:
            Inputs.click(*coords.NUKE)

    @staticmethod
    def fight() ->None:
        """Navigate to Fight Boss and click fight."""
        Navigation.menu("fight")
        Inputs.click(*coords.FIGHT)

class MoneyPit:
    @staticmethod
    def pit(loadout :int =0) -> None:
        """Throws money into the pit.

        Args:
	        loadout: The loadout you wish to equip before throwing gold
                   into the pit, for gear you wish to shock. Make
                   sure that you don't get cap-blocked by either using
                   the unassign setting in the game or swapping gear that
                   doesn't have e/m cap.
        """
        if Processing.check_pixel_color(*coords.IS_PIT_READY):
            if loadout:
                Inventory.loadout(loadout)
            Navigation.menu("pit")
            Inputs.click(*coords.PIT)
            Inputs.click(*coords.CONFIRM)

    @staticmethod
    def spin() -> None:
        """Spin the wheel."""
        Navigation.menu("pit")
        Inputs.click(*coords.SPIN_MENU)
        Inputs.click(*coords.SPIN)

class Adventure:
    class Const:
        current_zone = 0
        itopod_tier_counts = {}
        itopod_tier_map = {
            1: 0,
            2: 50,
            3: 100,
            4: 150,
            5: 200,
            6: 250,
            7: 300,
            8: 350,
            9: 400,
            10: 450,
            11: 500,
            12: 550,
            13: 600,
            14: 650,
            15: 700,
            16: 750,
            17: 800,
            18: 850,
            19: 900,
            20: 950,
        }
        itopod_ap_gained = 0
        itopod_kills = 0

        mega_buff_unlocked = False
        oh_shit_unlocked = False

    @staticmethod
    def set_zone(zone=0) -> None:
        """Go to an adventure zone.
 
        Args:
	        zone   : Zone to go to, 1 is safe zone, 2 is tutorial and so on.
                   Same zones than the wiki <3.
                   Set zone = 0 to go to highest zone.
        """
        Navigation.menu("adventure")
        Misc.waste_click()

        if zone < 0:
            print("zone too low, something went wrong")
            return
        elif zone == 0:
            Inputs.click(*coords.RIGHT_ARROW, Inputs.Const.MOUSE_RIGHT)
            Adventure.cz = Adventure.get_zone()
        elif zone == 1:
            Inputs.click(*coords.LEFT_ARROW, Inputs.Const.MOUSE_RIGHT)
            Adventure.cz = 1
        else:
            try:
                Adventure.cz = Adventure.get_zone()
                # If Adv zone returns 2, we can either be on tutorial zone or ITOPOD
                if Adventure.cz == 2:
                    Adventure.cz = 1
                    Inputs.click(*coords.LEFT_ARROW, Inputs.Const.MOUSE_RIGHT)
            except:
                Adventure.cz = 1
                Inputs.click(*coords.LEFT_ARROW, Inputs.Const.MOUSE_RIGHT)

            # We could check if current_zone == zone but this already does that as range(x, x) is empty
            for _ in range(Adventure.cz, zone):
                Inputs.click(*coords.RIGHT_ARROW, fast=True)

            # And we check we arrived properlee
            cur_zone = Adventure.get_zone()
            while zone < cur_zone:
                Inputs.click(*coords.LEFT_ARROW, fast=True)
                cur_zone = Adventure.get_zone()
            while zone > cur_zone:
                Inputs.click(*coords.RIGHT_ARROW, fast=True)
                cur_zone = Adventure.get_zone()
            Adventure.cz = cur_zone

    @staticmethod
    def get_zonename() -> str:
        """Gets the current Adv zone name"""
        Navigation.menu("adventure")
        Misc.waste_click()
        return Processing.ocr(*coords.OCR_ADV_ZONE)
    
    @staticmethod
    def get_zone() -> int:
        """Gets the current Adv zone number (starting at 1 for safe zone)"""
        zname = Adventure.get_zonename().lower()
        if (zname.count('.')) > 2: # If the name has various dots, it's the 1t0p0d, the itopOD, the ITOPOD or whatever the OCR feels like reading
            return -1
        try:
            return const.ZONE_MAP[zname]
        except KeyError:
            return 0 # Something impeded zone read, or the zone wasn't properly read or isn't accounted for on the zone map

    @staticmethod
    def itopod(start :int =None, end :int =None, *, blue :bool =False, lazy :bool =False) -> None:
        """Enter the ITOPOD.

        Args:
	        start: Starting ITOPOD floor. If unspecified, use optimal floor instead.
	        end  : Ending ITOPOD floor. If unspecified, assume 1600.
	        lazy : Use lazy floor shifter. For the laziest scripters.
	        blue : Use blue pills. But let's face it, those are actually Wiiagra.
        """
        Navigation.menu("adventure")
        Misc.waste_click()
        Adventure.cz = 0
        Inputs.click(*coords.ITOPOD)

        if start is None:
            Inputs.click(*coords.ITOPOD_AUTO)
        else:
            Inputs.click(*coords.ITOPOD_START)
            Inputs.send_string(str(start))
            Inputs.click(*coords.ITOPOD_END)
            if end is None:
                Inputs.send_string("1600")
            else:
                Inputs.send_string(str(end))
        
        if blue != Processing.check_pixel_color(*coords.ITOPOD_BLUE, '000000'): Inputs.click(*coords.ITOPOD_BLUE)
        if lazy != Processing.check_pixel_color(*coords.ITOPOD_LAZY, '000000'): Inputs.click(*coords.ITOPOD_LAZY)

        Inputs.click(*coords.ITOPOD_ENTER)
    
    @staticmethod
    def set_idle(active :bool =True) -> None:
        """Activate/Deactivate idle fighting mode.

        Args:
	        active: Whether to activate or deactivate idle fighting mode.
                  True means activate, False means deactivate.
        """
        Navigation.menu("adventure")
        Misc.waste_click()
        if active != Processing.check_pixel_color(*coords.IS_IDLE):
            Inputs.click(*coords.ABILITY_IDLE_MODE)
    
    @staticmethod
    def __reg_att() -> None:
        Navigation.menu("adventure")
        while not Processing.check_pixel_color(*coords.COLOR_REGULAR_ATTACK_READY):
            time.sleep(0.01)
        Inputs.click(*coords.ABILITY_REGULAR_ATTACK)

    @staticmethod
    def __fast_snipe(duration :int, *, regular :bool) -> None:
        endtime = time.time() + duration

        while time.time() < endtime or Processing.check_pixel_color(*coords.IS_ENEMY_ALIVE):
            if not regular: Adventure.kill_enemy()
            else:
                Adventure.__reg_att()

    @staticmethod
    def snipe(duration :int =0, *, bosses :bool =False, fast :bool =False, regular :bool =False) -> None:
        """Snipe enemies in current zone on adventure mode.
        WARNING: Unset idle before calling this and set it again when necessary.

        Args:
	        duration: Duration to snipe, in seconds. If this is zero, will snipe only one enemy.
	        bosses  : Set to True if you want to fight bosses only.
	        fast    : Set to True if your respawn is lower than 0.8s. Has no effect if you are sniping bosses.
	        regular : Set to True to use Regular Attack only. ITOPOD snipe style.
        """
        if fast and not bosses:
            Adventure.__fast_snipe(duration, regular)
            return
        
        endtime = time.time() + duration
        zone = Adventure.get_zone() # get adv zone here
        # print(zone)
        # print(list(const.ZONE_MAP)[zone-1])

        # Sniping loop
        while True:
            # Wait for enemy to respawn
            while not Processing.check_pixel_color(*coords.IS_ENEMY_ALIVE):
                time.sleep(0.01)

            # If not boss, skip enemy and restart sniping loop
            if bosses and not Processing.check_pixel_color(*coords.IS_BOSS_CROWN):
                Inputs.send_arrow(Inputs.Const.ARROW_RIGHT)
                Inputs.send_arrow(Inputs.Const.ARROW_LEFT)
                if zone != Adventure.get_zone(): # We messed up
                    Adventure.set_zone(zone)
                continue

            # Here we kill with regular attack
            if regular: 
                while True:
                    Adventure.__reg_att()
                    # If enemy dead, finish regular attack loop
                    if not Processing.check_pixel_color(*coords.IS_ENEMY_ALIVE): break
                    else: time.sleep(0.6)

            # Here we kill with full combo
            else: Adventure.kill_enemy()

            # Check if exceeded duration
            if time.time() > endtime: break

    @staticmethod
    def snipe_( # TODO
        zone :int,
        duration :int,
        once :bool =False,
        highest :bool =False,
        bosses :bool =False,
        manual :bool =False,
        fast :bool =False) -> None:
        """Go to adventure and snipe bosses in specified zone.

        Args:
	        zone: Zone to snipe, 0 is safe zone, 1 is turorial and so on.
                If 0, it will use the current zone (to maintain guffin counter)
	        duration: The duration in minutes the sniping will run before
                    returning.
	        once: If true it will only kill one boss before returning.
	        highest: If set to true, it will go to your highest available
                   non-titan zone.
	        bosses: If set to true, it will only kill bosses
	        manual: If set to true it will use all available abilities to kill the enemy.
                  In addition it will return after killing one enemy.
	        fast  : If your respawn is lower than your attack speed, use
                  this to remove the overhead from check_pixel_color().
                  It should give you higher xp/h. Remember that move CD
                  is capped at 0.8s, so there's no reason to go lower.
        """
        Navigation.menu("adventure")
        if highest:
            Inputs.click(*coords.LEFT_ARROW, Inputs.Const.MOUSE_RIGHT)
            Inputs.click(*coords.RIGHT_ARROW, Inputs.Const.MOUSE_RIGHT)
        elif zone > 0 and zone != Adventure.cz:
            Inputs.click(*coords.LEFT_ARROW, Inputs.Const.MOUSE_RIGHT)
            for _ in range(zone):
                Inputs.click(*coords.RIGHT_ARROW, fast=True)
        Adventure.cz = zone
        Inputs.click(625, 500)  # click somewhere to move tooltip
        
        if Processing.check_pixel_color(*coords.IS_IDLE):
            Inputs.click(*coords.ABILITY_IDLE_MODE)
        
        end = time.time() + duration * 60
        while time.time() < end:
            if fast:
                Inputs.click(*coords.ABILITY_REGULAR_ATTACK, fast=True)
            else:
                Inputs.click(625, 500)  # click somewhere to move tooltip
                if Adventure.is_enemy_alive():
                    if bosses:
                        if Processing.check_pixel_color(*coords.IS_BOSS_CROWN):
                            enemy_alive = True
                            if manual:
                                Adventure.kill_enemy()
                            else:
                                while enemy_alive:
                                    enemy_alive = Adventure.is_enemy_alive()
                                    if Processing.check_pixel_color(*coords.COLOR_REGULAR_ATTACK_READY):
                                        Inputs.click(*coords.ABILITY_REGULAR_ATTACK)
                                    time.sleep(0.1)
                            if once:
                                break
                        else:
                            # Send left arrow and right arrow to refresh monster.
                            Inputs.send_arrow(Inputs.Const.ARROW_RIGHT)
                            Inputs.send_arrow(Inputs.Const.ARROW_LEFT)
                    else:
                        if manual:
                            Adventure.kill_enemy()
                            return
                        else:
                            Inputs.click(*coords.ABILITY_REGULAR_ATTACK)
            time.sleep(0.01)
        
        Inputs.click(*coords.ABILITY_IDLE_MODE)
    
    @staticmethod
    def old_itopod_snipe(duration :int, auto :bool =False, fast :bool =False) -> None: # TODO
        """Manually snipes ITOPOD for increased speed PP/h.
        
        Args:
	        duration: Duration in seconds to snipe, before toggling idle mode
                    back on and returning.
	        auto    : Make sure you're on the optimal floor even if you're
                    already in the ITOPOD
	        fast    : If your respawn is lower than your attack speed, use
                    this to remove the overhead from check_pixel_color().
                    It should give you higher xp/h. Remember that move CD
                    is capped at 0.8s, so there's no reason to go lower.
        """
        end = time.time() + duration
        Adventure.cz = 0
        Navigation.menu("adventure")
        Inputs.click(625, 500)  # click somewhere to move tooltip
        
        # check if we're already in ITOPOD, otherwise enter
        # if auto is true, re-enter ITOPOD to make sure floor is optimal
        if auto or not Processing.check_pixel_color(*coords.IS_ITOPOD_ACTIVE):
            Inputs.click(*coords.ITOPOD)
            Inputs.click(*coords.ITOPOD_END)
            # set end to 0 in case it's higher than start
            Inputs.send_string("0")
            Inputs.click(*coords.ITOPOD_AUTO)
            Inputs.click(*coords.ITOPOD_ENTER)
        
        if Processing.check_pixel_color(*coords.IS_IDLE):
            Inputs.click(*coords.ABILITY_IDLE_MODE)
        
        while time.time() < end:
            if fast:
                Inputs.click(*coords.ABILITY_REGULAR_ATTACK, fast=True)
                continue
            if (Processing.check_pixel_color(*coords.IS_ENEMY_ALIVE) and
               Processing.check_pixel_color(*coords.COLOR_REGULAR_ATTACK_READY)):
                Inputs.click(*coords.ABILITY_REGULAR_ATTACK)
            else:
                time.sleep(0.01)
        
        Inputs.click(*coords.ABILITY_IDLE_MODE)
    
    @staticmethod
    def is_enemy_alive() -> bool:
        return (not Processing.check_pixel_color(*coords.IS_DEAD)) or Processing.check_pixel_color(*coords.IS_ENEMY_ALIVE_2)

    @staticmethod
    def kill_enemy() -> None: # TODO
        """Attempt to kill enemy in adventure using abilities."""
        start = time.time()
        Adventure.set_idle(False)
        while not Adventure.is_enemy_alive():
            time.sleep(.1)
            if time.time() > start + 5:
                print("Couldn't detect enemy in kill_enemy()")
                return
        queue = deque(Adventure.get_ability_queue())
        while Adventure.is_enemy_alive():
            if not queue:
                queue = deque(Adventure.get_ability_queue())

            ability = queue.popleft()
            Adventure.use_ability(ability)
            Misc.waste_click()
            time.sleep(userset.LONG_SLEEP)
            
            while not Processing.check_pixel_color(
                coords.ABILITY_ROW1X, coords.ABILITY_ROW1Y,
                coords.ABILITY_ROW1_READY_COLOR
            ) : time.sleep(0.03)
        
    @staticmethod
    def get_drops(*, gold :bool =False) -> List[str]:
        logs = Processing.ocr(*coords.OCR_ADV_LOG).splitlines()
        found_last = False
        drops = []

        for x in reversed(logs):
            if not found_last and "dropped" in x: found_last = True
            if found_last:
                if not "dropped" in x: break
                if gold or not "gold!" in x:
                    spl = x.split("dropped ")[1].split("!")
                    if len(spl) > 1: s = spl[0]
                    else: s = spl[0]
                    drops.append(s)
        
        drops.reverse()
        return drops

    @staticmethod
    def get_titan_status() -> List[int]: # TODO
        """Check to see if any titans are ready."""
        Inputs.click(*coords.MENU_ITEMS["adventure"], Inputs.Const.MOUSE_RIGHT)
        text = Processing.ocr(*coords.OCR_TITAN_RESPAWN).lower()
        ready = []
        i = 1
        for line in text.split('\n'):
            if line == '' or line == '\n':
                continue
            if "ready" in line:
                ready.append(i)
            i += 1
        return ready
    
    @staticmethod
    def kill_titan(target :int, mega :bool =True) -> None: # TODO
        """Attempt to kill the target titan.
        
        Args:
	        target: The id of the titan you wish to kill. 1 for GRB, 2 for GCT and so on.
	        mega  : Use Mega Buff
        """
        Navigation.menu("adventure")
        if Processing.check_pixel_color(*coords.IS_IDLE):
            Inputs.click(*coords.ABILITY_IDLE_MODE)
        
        Inputs.click(*coords.LEFT_ARROW, Inputs.Const.MOUSE_RIGHT)
        charge = False
        parry = False
        if mega:
            while not Processing.check_pixel_color(*coords.COLOR_MEGA_BUFF_READY) or not charge or not parry:
                queue = Adventure.get_ability_queue()
                Inputs.click(625, 600)
                if 2 in queue and not parry:
                    x = coords.ABILITY_ROW1X + 2 * coords.ABILITY_OFFSETX
                    y = coords.ABILITY_ROW1Y
                    Inputs.click(x, y)
                    parry = True
                    time.sleep(1)  # wait for global cooldown
                if 9 in queue and not charge:
                    x = coords.ABILITY_ROW2X + (9 - 5) * coords.ABILITY_OFFSETX
                    y = coords.ABILITY_ROW2Y
                    Inputs.click(x, y)
                    charge = True
                    time.sleep(1)  # wait for global cooldown
                time.sleep(userset.MEDIUM_SLEEP)
        
        else:
            while not Processing.check_pixel_color(*coords.COLOR_ULTIMATE_BUFF_READY) or not charge or not parry:
                queue = Adventure.get_ability_queue()
                Inputs.click(625, 600)
                if 2 in queue and not parry:
                    x = coords.ABILITY_ROW1X + 2 * coords.ABILITY_OFFSETX
                    y = coords.ABILITY_ROW1Y
                    Inputs.click(x, y)
                    parry = True
                    time.sleep(1)  # wait for global cooldown
                if 9 in queue and not charge:
                    x = coords.ABILITY_ROW2X + 4 * coords.ABILITY_OFFSETX
                    y = coords.ABILITY_ROW2Y
                    Inputs.click(x, y)
                    charge = True
                    time.sleep(1)  # wait for global cooldown
                time.sleep(userset.MEDIUM_SLEEP)
        
        buffs = [2, 9]
        print("Waiting for charge and parry to be ready")
        while not all(x in Adventure.get_ability_queue() for x in buffs):
            time.sleep(.5)
        
        for _ in range(const.TITAN_ZONE[target - 1]):
            Inputs.click(*coords.RIGHT_ARROW, fast=True)
        Adventure.cz = const.TITAN_ZONE[target - 1]
        time.sleep(userset.LONG_SLEEP)
        start = time.time()
        while not Adventure.is_enemy_alive():  # wait for titan to spawn
            time.sleep(0.05)
            if time.time() > start + 5:
                print("Couldn't detect enemy in kill_titan()")
                return
        
        queue = deque(Adventure.get_ability_queue())
        while Adventure.is_enemy_alive():
            if not queue:
                queue = deque(Adventure.get_ability_queue())
            
            ability = queue.popleft()
            if ability <= 4:
                x = coords.ABILITY_ROW1X + ability * coords.ABILITY_OFFSETX
                y = coords.ABILITY_ROW1Y
            
            if ability >= 5 and ability <= 10:
                x = coords.ABILITY_ROW2X + (ability - 5) * coords.ABILITY_OFFSETX
                y = coords.ABILITY_ROW2Y
            
            if ability > 10:
                x = coords.ABILITY_ROW3X + (ability - 11) * coords.ABILITY_OFFSETX
                y = coords.ABILITY_ROW3Y
            
            Inputs.click(x, y)
            time.sleep(userset.LONG_SLEEP)
            color = Inputs.get_pixel_color(coords.ABILITY_ROW1X,
                                           coords.ABILITY_ROW1Y)
            
            while color != coords.ABILITY_ROW1_READY_COLOR:
                time.sleep(0.05)
                color = Inputs.get_pixel_color(coords.ABILITY_ROW1X,
                                               coords.ABILITY_ROW1Y)
    
    def use_ability(ability) -> None:
        if ability <= 4:
            x = coords.ABILITY_ROW1X + ability * coords.ABILITY_OFFSETX
            y = coords.ABILITY_ROW1Y
        
        if ability >= 5 and ability <= 10:
            x = coords.ABILITY_ROW2X + (ability - 5) * coords.ABILITY_OFFSETX
            y = coords.ABILITY_ROW2Y
        
        if ability > 10:
            x = coords.ABILITY_ROW3X + (ability - 11) * coords.ABILITY_OFFSETX
            y = coords.ABILITY_ROW3Y
        
        Inputs.click(x, y)

    @staticmethod
    def get_ability_queue() -> List[int]: # TODO
        """Return a queue of usable abilities."""
        ready = []
        queue = []
        
        # Add all abilities that are ready to the ready array
        for i in range(1, 16):
            if i <= 4:
                x = coords.ABILITY_ROW1X + i * coords.ABILITY_OFFSETX
                y = coords.ABILITY_ROW1Y
                color = Inputs.get_pixel_color(x, y)
                if color == coords.ABILITY_ROW1_READY_COLOR:
                    ready.append(i)
            if i >= 5 and i <= 10:
                if Adventure.Const.mega_buff_unlocked and i == 6:
                    continue
                x = coords.ABILITY_ROW2X + (i - 5) * coords.ABILITY_OFFSETX
                y = coords.ABILITY_ROW2Y
                color = Inputs.get_pixel_color(x, y)
                if color == coords.ABILITY_ROW2_READY_COLOR:
                    ready.append(i)
            if i > 10:
                x = coords.ABILITY_ROW3X + (i - 11) * coords.ABILITY_OFFSETX
                y = coords.ABILITY_ROW3Y
                color = Inputs.get_pixel_color(x, y)
                if color == coords.ABILITY_ROW3_READY_COLOR:
                    ready.append(i)
        
        if 15 in ready:
            Adventure.Const.oh_shit_unlocked = True
        if 14 in ready:
            Adventure.Const.mega_buff_unlocked = True
        # heal if we need to heal
        if Processing.check_pixel_color(*coords.PLAYER_HEAL_THRESHOLD):
            if 15 in ready:
                queue.append(15)
            elif 12 in ready:
                queue.append(12)
            elif 7 in ready:
                queue.append(7)
        
        # check if offensive buff and ultimate buff are both ready
        buffs = [8, 10]
        if 14 in ready:
            queue.append(14)
        elif all(i in ready for i in buffs) and not Adventure.Const.mega_buff_unlocked:
            queue.extend(buffs)
        
        d = coords.ABILITY_PRIORITY
        # Sort the abilities by the set priority
        abilities = sorted(d, key=d.get, reverse=True)
        # Only add the abilities that are ready to the queue
        queue.extend([a for a in abilities if a in ready])
        
        # If nothing is ready, return a regular attack
        if not queue:
            queue.append(0)
        return queue
    
    @staticmethod
    def old_itopod_ap(duration :int) -> None: # TODO
        """Abuse an oversight in the kill counter for AP rewards for mucher higher AP/h in ITOPOD.
        If you use this method, make sure you do not retoggle idle mode in adventure in other parts
        of your script. If you have to, make sure to empty itopod_tier_counts with:
        itopod_tier_counts = {}
        
        Args:
	        duration: Duration in seconds to run, before toggling idle mode
                    back on and returning.
        """
        print("WARNING: itopod_ap() is largely untested")
        end = time.time() + duration * 60
        Adventure.cz = 0
        Navigation.menu("adventure")
        Inputs.click(625, 500)  # click somewhere to move tooltip
        if Processing.check_pixel_color(*coords.IS_IDLE):
            Inputs.click(*coords.ABILITY_IDLE_MODE)
        # check if we're already in ITOPOD, otherwise enter
        if not Adventure.Const.itopod_tier_counts:
            for tier, floor in Adventure.Const.itopod_tier_map.items():
                Inputs.click(*coords.ITOPOD)
                Inputs.click(*coords.ITOPOD_START)
                Inputs.send_string(floor)
                # set end to 0 in case it's higher than start
                Inputs.click(*coords.ITOPOD_ENTER)
                Inputs.click(*coords.ADVENTURE_TOOLTIP)
                count = Processing.remove_letters(Processing.ocr(*coords.OCR_AP_KILL_COUNT))
                print(f"Tier {tier}: {count}")
                try:
                    count = int(count)
                except ValueError:
                    print(f"couldn't convert '{count}' to int")
                Adventure.Const.itopod_tier_counts[tier] = count
        print(Adventure.Const.itopod_tier_counts)
        while time.time() < end:
            next_tier = min(Adventure.Const.itopod_tier_counts, key=Adventure.Const.itopod_tier_counts.get)
            print(f"going to itopod tier {next_tier}")
            Inputs.click(*coords.ITOPOD)
            Inputs.click(*coords.ITOPOD_START)
            Inputs.send_string(Adventure.Const.itopod_tier_map[next_tier])
            # set end to 0 in case it's higher than start
            Inputs.click(*coords.ITOPOD_ENTER)
            time.sleep(userset.LONG_SLEEP)
            kc = Adventure.Const.itopod_tier_counts[next_tier]
            while kc > 0:
                if Processing.check_pixel_color(*coords.IS_ENEMY_ALIVE):
                    Inputs.click(*coords.ABILITY_REGULAR_ATTACK)
                    
                    Adventure.Const.itopod_kills += 1
                    kc -= 1
                    if kc > 0:
                        time.sleep(.7 - userset.MEDIUM_SLEEP)  # Make sure we wait long enough
                    for tier, count in Adventure.Const.itopod_tier_counts.items():
                        Adventure.Const.itopod_tier_counts[tier] -= 1
                        if Adventure.Const.itopod_tier_counts[tier] < 1:
                            Adventure.Const.itopod_tier_counts[tier] = 40 - tier
                else:
                    time.sleep(0.06)
            Adventure.Const.itopod_ap_gained += 1
            print(f"Kills: {Adventure.Const.itopod_kills}\nAP gained: {Adventure.Const.itopod_ap_gained}")
        return

class Inventory:
    @staticmethod
    def merge_equipment() -> None:
        """Navigate to inventory and merge equipment."""
        Navigation.menu("inventory")
        for slot in coords.EQUIPMENT_SLOTS:
            if slot == "cube":
                return
            Inputs.click(*coords.EQUIPMENT_SLOTS[slot])
            Inputs.send_string("d")
    
    @staticmethod
    def boost_equipment(boost_cube :bool =True) -> None:
        """Boost all equipment.
        
        Args:
	        boost_cube: If True (default), will boost cube after all equipment
                      has been boosted.
        """
        Navigation.menu("inventory")
        for slot in coords.EQUIPMENT_SLOTS:
            if boost_cube and slot == "cube":
                Inventory.boost_cube()
                return
            Inputs.click(*coords.EQUIPMENT_SLOTS[slot])
            Inputs.send_string("a")
    
    @staticmethod
    def boost_cube() -> None:
        """Boost cube."""
        Navigation.menu("inventory")
        Inputs.click(*coords.EQUIPMENT_SLOTS["cube"], Inputs.Const.MOUSE_RIGHT)
    
    @staticmethod
    def loadout(target :int) -> None:
        """Equip a loadout.
        
        Args:
	        target: The loadout to be equiped
        """
        Navigation.menu("inventory")
        Inputs.click(*coords.LOADOUT[target])
    
    @staticmethod
    def get_inventory_slots(slots :int) -> List[Tuple[int, int]]:
        """Get coords for inventory slots from 1 to slots."""
        point = namedtuple("p", ("x", "y"))
        i = 1
        row = 1
        x_pos, y_pos = coords.INVENTORY_SLOTS
        res = []
        
        while i <= slots:
            x = x_pos + (i - (12 * (row - 1))) * 50
            y = y_pos + ((row - 1) * 50)
            res.append(point(x, y))
            if i % 12 == 0:
                row += 1
            i += 1
        return res
    
    @staticmethod
    def merge_inventory(slots :int) -> None:
        """Merge all inventory slots starting from 1 to slots.
        
        Args:
	        slots: The amount of slots you wish to merge
        """
        Navigation.menu("inventory")
        coord = Inventory.get_inventory_slots(slots)
        for slot in coord:
            Inputs.click(*slot)
            Inputs.send_string("d")
    
    @staticmethod
    def boost_inventory(slots :int) -> None:
        """Merge all inventory slots starting from 1 to slots.
        
        Args:
	        slots: The amount of slots you wish to merge
        """
        Navigation.menu("inventory")
        coord = Inventory.get_inventory_slots(slots)
        for slot in coord:
            Inputs.click(*slot)
            Inputs.send_string("a")
    
    @staticmethod
    def transform_slot(slot :int, threshold :float =0.8, consume :bool =False) -> None:
        """Check if slot is transformable and transform if it is.
        Be careful using this, make sure the item you want to transform is
        not protected, and that all other items are protected, this might
        delete items otherwise. Another note, consuming items will show
        a special tooltip that will block you from doing another check
        for a few seconds, keep this in mind if you're checking multiple
        slots in succession.
        
        Args:
	        slot     : The slot you wish to transform, if possible
	        threshold: The fuzziness in the image search, I recommend a value
                     between 0.7 - 0.95.
	        consume  : Set to true if item is consumable instead.
        """
        Navigation.menu("inventory")
        slot = Inventory.get_inventory_slots(slot)[-1]
        Inputs.click(*slot)
        time.sleep(userset.SHORT_SLEEP)
        
        if consume:
            coord = Processing.image_search(Window.x, Window.y, Window.x + 960, Window.y + 600,
                                        Processing.get_file_path("images", "consumable.png"), threshold)
        else:
            coord = Processing.image_search(Window.x, Window.y, Window.x + 960, Window.y + 600,
                                        Processing.get_file_path("images", "transformable.png"), threshold)
        
        if coord:
            Inputs.ctrl_click(*slot)

class Augmentation:
    @staticmethod
    def assign_energy(augments :Dict[str, float], energy :int) -> None:
        """Dump energy into augmentations.
        
        Args:
	        augments: Dictionary that contains which augments you wish to use and
                    a ratio that tells how much of the total energy you
                    allocated you wish to send. Example:
                    {"SS": 0, "DS": 0, "MI": 0, "DTMT": 0, "CI": 0, "M": 0,
                     "SM": 0, "AA": 0, "EB": 0, "CS": 0, "AE": 0, "ES": 0,
                     "LS": 0.9, "QSL": 0.1}
	        Energy: The total amount of energy you want to use for all augments.
        """
        Navigation.menu("augmentations")
        for k in augments:
            val = math.floor(augments[k] * energy)
            Misc.set_input(val)
            # Scroll down if we have to.
            bottom_augments = ["AE", "ES", "LS", "QSL"]
            i = 0
            if k in bottom_augments:
                color = Inputs.get_pixel_color(*coords.AUG_SCROLL_SANITY_BOT)
                while color not in coords.SANITY_AUG_SCROLL_COLORS:
                    Inputs.click(*coords.AUG_SCROLL_BOT)
                    time.sleep(userset.MEDIUM_SLEEP)
                    color = Inputs.get_pixel_color(*coords.AUG_SCROLL_SANITY_BOT)
                    i += 1
                    if i > 5 and i <= 10:  # Safeguard if something goes wrong with augs
                        Navigation.current_menu = ""
                        Navigation.menu("augmentations")
                    elif i > 10:
                        print("Couldn't assign augments")
                        break
            
            else:
                color = Inputs.get_pixel_color(*coords.AUG_SCROLL_SANITY_TOP)
                while color not in coords.SANITY_AUG_SCROLL_COLORS:
                    Inputs.click(*coords.AUG_SCROLL_TOP)
                    time.sleep(userset.MEDIUM_SLEEP)
                    color = Inputs.get_pixel_color(*coords.AUG_SCROLL_SANITY_TOP)
                    i += 1
                    if i > 5 and i <= 10:  # Safeguard if something goes wrong with augs
                        Navigation.current_menu = ""
                        Navigation.menu("augmentations")
                    elif i > 10:
                        print("Couldn't assign augments")
                        break
            Inputs.click(*coords.AUGMENT[k])

class AdvancedTraining:
    @staticmethod
    def assign_energy(energy :int, ability :int =0) -> None:
        """Assign energy to adanced training.
        
        Args:
	        energy : Set the total energy to assign to AT.
	        ability: The AT ability to be trained.
                   If this is zero, it'll split the energy evenly between
                   Adv Toughness, Adv Power, Wandoos Energy and Wandoos Magic.
                   Splitting energy is the default behavior.
        """
        Navigation.menu("advtraining")
        if ability == 0:
            energy = energy // 4
            Misc.set_input(energy)
            Inputs.click(*coords.ADV_TRAINING_POWER)
            Inputs.click(*coords.ADV_TRAINING_TOUGHNESS)
            Inputs.click(*coords.ADV_TRAINING_WANDOOS_ENERGY)
            Inputs.click(*coords.ADV_TRAINING_WANDOOS_MAGIC)
        
        else:
            Misc.set_input(energy)
            if ability == 1:
                Inputs.click(*coords.ADV_TRAINING_TOUGHNESS)
            if ability == 2:
                Inputs.click(*coords.ADV_TRAINING_POWER)
            if ability == 3:
                Inputs.click(*coords.ADV_TRAINING_BLOCK)
            if ability == 4:
                Inputs.click(*coords.ADV_TRAINING_WANDOOS_ENERGY)
            if ability == 5:
                Inputs.click(*coords.ADV_TRAINING_WANDOOS_MAGIC)

class TimeMachine:
    @staticmethod
    def assign_resources(e :int, m :int =0, magic :bool =False) -> None: ##
        """Add energy and/or magic to TM.
        
        Example: TimeMachine.time_machine(1000, 2000)
                 TimeMachine.time_machine(1000, magic=True)
                 TimeMachine.time_machine(1000)
        
        First example will add 1000 energy and 2000 magic to TM.
        Second example will add 1000 energy and 1000 magic to TM.
        Third example will add 1000 energy to TM.
        
        Args:
	        e: The amount of energy to put into TM.
	        m: The amount of magic to put into TM, if this is 0, it will use the
             energy value to save unnecessary clicks to the input box.
	        magic: Set to true if you wish to add magic as well
        """
        Navigation.menu("timemachine")
        Misc.set_input(e)
        Inputs.click(*coords.TM_SPEED)
        if magic or m:
            if m:
                Misc.set_input(m)
            Inputs.click(*coords.TM_MULT)

class BloodMagic:
    @staticmethod
    def blood_magic(target :int) -> None:
        """Assign magic to BM.
        
        Args:
	        target: Will cap all rituals till the target ritual
                  Usually run as blood_magic(8)
        """
        Navigation.menu("bloodmagic")
        for i in range(target):
            Inputs.click(*coords.BM[i])
    
    @staticmethod
    def toggle_auto_spells(number :bool =True, drop :bool =True, gold :bool =True) -> None:
        """Enable/Disable autospells
        
        Args:
	        number, drop, gold: Spells to be enabled or disabled.
                              If True, enable the spell. If False, disable the spell.
                              If None, ignore the spell.
        """
        Navigation.spells()
        Inputs.click(600, 600)  # move tooltip
        
        if number is not None:
            number_active = Processing.check_pixel_color(*coords.COLOR_BM_AUTO_NUMBER)
            if (number and not number_active) or (not number and number_active):
                Inputs.click(*coords.BM_AUTO_NUMBER)
        if drop is not None:
            drop_active = Processing.check_pixel_color(*coords.COLOR_BM_AUTO_DROP)
            if (drop and not drop_active) or (not drop and drop_active):
                Inputs.click(*coords.BM_AUTO_DROP)
        
        if gold is not None:
            gold_active = Processing.check_pixel_color(*coords.COLOR_BM_AUTO_GOLD)
            if (gold and not gold_active) or (not gold and gold_active):
                Inputs.click(*coords.BM_AUTO_GOLD)
    
    @staticmethod
    def get_spells_ready() -> List[int]:
        """Check which spells are ready to cast.
        
        Returns a list with integers corresponding to which spell is ready. The values on the
        list can be:
            1 - Iron pill
            2 - MacGuffin alpha
            3 - MacGuffin beta
        """
        if Processing.check_pixel_color(*coords.COLOR_SPELL_READY):
            Navigation.spells()
            Inputs.click(*coords.BM_PILL, Inputs.Const.MOUSE_RIGHT)
            spells = []
            res = Processing.ocr(*coords.OCR_BM_SPELL_TEXT)
            if "cooldown: 0.0s" in res.lower():
                spells.append(1)
            
            Inputs.click(*coords.BM_GUFFIN_A, Inputs.Const.MOUSE_RIGHT)
            res = Processing.ocr(*coords.OCR_BM_SPELL_TEXT)
            if "cooldown: 0.0s" in res.lower():
                spells.append(2)
            
            Inputs.click(*coords.BM_GUFFIN_B, Inputs.Const.MOUSE_RIGHT)
            res = Processing.ocr(*coords.OCR_BM_SPELL_TEXT)
            if "cooldown: 0.0s" in res.lower():
                spells.append(3)
            
            return spells
        else:
            return []
    
    @staticmethod
    def cast_spell(target :int) -> None:
        """Cast target spell.
        
        This method will allocate any idle magic into BM and wait for the
        time set in usersettings.py. Remember to re-enable auto spells after
        calling this method, using toggle_auto_spells().
        
        Args:
	        number: The spell to be cast. Possible values are:
            1 - Iron pill
            2 - MacGuffin alpha
            3 - MacGuffin beta
        """
        if Processing.check_pixel_color(*coords.COLOR_SPELL_READY):
            targets = [0, coords.BM_PILL, coords.BM_GUFFIN_A, coords.BM_GUFFIN_B]
            start = time.time()
            BloodMagic.blood_magic(8)
            BloodMagic.toggle_auto_spells(False, False, False)  # disable all auto spells
            
            if userset.SPELL == 0:  # Default to 5 mins if not set
                duration = 300
            else:
                duration = userset.SPELL
            
            while time.time() < start + duration:
                print(f"Sniping itopod for {duration} seconds while waiting to cast spell.")
                Adventure.old_itopod_snipe(duration)
            Navigation.spells()
            Inputs.click(*targets[target])

class Wandoos:
    @staticmethod
    def cap_dumps(energy :bool =True, magic :bool =False) -> None:
        """Assign energy and/or magic to wandoos.
        
        Args:
	        energy: Assign energy to Wandoos (default: True)
	        magic : Assign magic to Wandoos  (default: False)
        """
        Navigation.menu("wandoos")
        if energy:
            Inputs.click(*coords.WANDOOS_ENERGY)
        if magic:
            Inputs.click(*coords.WANDOOS_MAGIC)
    
    @staticmethod
    def set_wandoos(version :int) -> None:
        """Set wandoos version.
        
        Args:
	        version: Wandoos version of choice. Possible values are:
                   0 : Wandoos 98
                   1 : Wandoos Meh
                   2 : Wandoos XL
        """
        Navigation.menu("wandoos")
        Inputs.click(*coords.WANDOOS_VERSION[version])
        Navigation.confirm()
    
    @staticmethod
    def get_bb_status(magic :bool =False) -> bool:
        """Check if wandoos is currently fully BB'd.
        
        Args:
	        magic: If True, check if Wandoos magic is BB'd
                 If False (default), check if Wandoos energy is BB'd
        """
        Navigation.menu("wandoos")
        if magic:
            return Processing.check_pixel_color(*coords.COLOR_WANDOOS_MAGIC_BB)
        return Processing.check_pixel_color(*coords.COLOR_WANDOOS_ENERGY_BB)

class NGU:
    @staticmethod
    def assign(value :int, targets :List[int], magic :bool =False) -> None:
        """Assign energy/magic to NGU's.
        
        Args:
	        value: the amount of energy/magic that will get split over all NGUs.
	        targets: Array of NGU's to use (1-9).
	        magic: Set to true if these are magic NGUs
        """
        if len(targets) > 9:
            raise RuntimeError("Passing too many NGU's to assign_ngu," +
                               " allowed: 9, sent: " + str(len(targets)))
        if magic: Navigation.ngu_magic()
        else: Navigation.menu("ngu")
        
        Misc.set_input(value // len(targets))
        for i in targets:
            NGU = coords.Pixel(coords.NGU_PLUS.x, coords.NGU_PLUS.y + i * 35)
            Inputs.click(*NGU)
    
    @staticmethod
    def cap(targets :List[int] =None, magic :bool =False, cap_all :bool =True) -> None:
        """Cap NGUs.

        Args:
	        targets: The NGU's you wish to cap
	        magic: Set to true if these are magic NGU's
	        cap_all: Set to true if you wish to cap all NGU's
        """
        targets = targets or []
        if magic:
            Navigation.ngu_magic()
        else:
            Navigation.menu("ngu")
        
        for target in targets:
            NGU = coords.Pixel(coords.NGU_CAP.x, coords.NGU_CAP.y + target * 35)
            Inputs.click(*NGU)
        
        if cap_all and not targets:
            Inputs.click(*coords.NGU_CAP_ALL)
    
    @staticmethod
    def set_overcap(value :int) -> None:
        """Set the amount you wish to overcap your NGU's."""
        Navigation.menu("ngu")
        Inputs.click(*coords.NGU_OVERCAP)
        Inputs.send_string(value)

class Yggdrasil:
    @staticmethod
    def harvest(eat_all :bool =False, equip :int =0) -> None:
        """Navigate to inventory and handle fruits.
        
        Args:
	        eat_all : Set to true if you're rebirthing, it will force eat all
                   fruit.
	        equip   : Equip loadout with given index. Don't change if zero.
        """
        if equip:
            Misc.reclaim_all()
            Inventory.loadout(equip)
        
        Navigation.menu("yggdrasil")
        if eat_all:
            Inputs.click(*coords.YGG_EAT_ALL)
        else:
            Inputs.click(*coords.HARVEST)

class GoldDiggers:
    @staticmethod
    def activate(targets :List[int] =const.DEFAULT_DIGGER_ORDER, deactivate :bool =False) -> None:
        """Activate diggers.
        
        Args:
	        targets: Array of diggers to use from 1-12. Example: [1, 2, 3, 4, 9].
	        deactivate: Set to True if you wish to deactivate these
                    diggers otherwise it will just try to up the cap.
        """
        Navigation.menu("digger")
        for i in targets:
            page = ((i - 1) // 4)
            item = i - (page * 4)
            Inputs.click(*coords.DIG_PAGE[page])
            if deactivate:
                Inputs.click(*coords.DIG_ACTIVE[item])
            else:
                Inputs.click(*coords.DIG_CAP[item])
    
    @staticmethod
    def deactivate_all() -> None:
        """Click deactivate all in digger menu."""
        Navigation.menu("digger")
        Inputs.click(*coords.DIG_DEACTIVATE_ALL)
    
    @staticmethod
    def level_all() -> None:
        """Level all diggers."""
        Navigation.menu("digger")
        for page in coords.DIG_PAGE:
            Inputs.click(*page)
            for digger in coords.DIG_LEVEL:
                Inputs.click(*digger, Inputs.Const.MOUSE_RIGHT)

class BeardsOfPower:
    """This class is highly tentative"""

    class Const:
        ACTIVE_BOX = coords.Pixel(316,234)

        BEARD_BUTTON_1 = coords.Pixel(313,318)
        BEARD_BUTTON_2 = coords.Pixel(338,318)
        BEARD_BUTTON_7 = coords.Pixel(325,392)
        BEARD_BUTTON_Y_OFFSET = 25

        BEARD_LIST_DROPDOWN = coords.Pixel(470,200)
        BEARD_LIST_FIRST = coords.Pixel(314,228)
        BEARD_LIST_Y_OFFSET = 20

        NUM_ACTIVE_OCR = coords.OCRBox(820,123,870,143)
        TEMP_LEVEL_OCR = coords.OCRBox(510,230,590,250)
        PERM_LEVEL_OCR = coords.OCRBox(380,100,660,250)
        BEARD_BAR = coords.Pixel(680,280)
    
    @staticmethod
    def select(beard :int) -> None:
        """Selects a beard."""
        Navigation.menu("beard")
        if beard == 7:
            Inputs.click(*BeardsOfPower.Const.BEARD_BUTTON_7)
        elif beard%2 == 1:
            Inputs.click(
                BeardsOfPower.Const.BEARD_BUTTON_1.x,
                BeardsOfPower.Const.BEARD_BUTTON_1.y + (beard//2) * BeardsOfPower.Const.BEARD_BUTTON_Y_OFFSET
            )
        else:
            Inputs.click(
                BeardsOfPower.Const.BEARD_BUTTON_2.x,
                BeardsOfPower.Const.BEARD_BUTTON_2.y + ((beard//2) -1) * BeardsOfPower.Const.BEARD_BUTTON_Y_OFFSET
            )

    @staticmethod
    def is_active(beard :int) -> bool:
        """Returns whether the selected beard is active."""
        BeardsOfPower.select(beard)
        return Processing.check_pixel_color(*BeardsOfPower.Const.ACTIVE_BOX, Color.BLACK.hex())

    @staticmethod
    def activate(beard :int) -> None:
        """Activates a beard."""
        if not BeardsOfPower.is_active(beard):
            Inputs.click(*BeardsOfPower.Const.ACTIVE_BOX)

    @staticmethod
    def deactivate(beard :int) -> None:
        """Deactivates a beard."""
        if BeardsOfPower.is_active(beard):
            Inputs.click(*BeardsOfPower.Const.ACTIVE_BOX)

    @staticmethod
    def get_temp(beard :int) -> int:
        """Returns beard's temporal level."""
        BeardsOfPower.select(beard)
        return Processing.ocr_number(*BeardsOfPower.Const.TEMP_LEVEL_OCR)

    @staticmethod
    def get_perm(beard :int) -> int:
        """Returns beard's permanent level."""
        BeardsOfPower.select(beard)
        Inputs.click(*BeardsOfPower.Const.BEARD_BAR)
        s = Processing.ocr(*BeardsOfPower.Const.PERM_LEVEL_OCR)
        s = s.splitlines()

        i = 0
        while i < len(s):
            if "Math For Nerds" == s[i]:
                break
            i+=1
        
        a = Processing.get_numbers(s[i+1])
        while len(a) < 1:
            i+=1
            a = Processing.get_numbers(s[i+1])

        Misc.waste_click()

        return a[0]

    @staticmethod
    def get_active() -> Tuple[int, int]:
        """Gets the current and maximum active numbers."""
        Navigation.menu("beard")
        s = Processing.ocr(*BeardsOfPower.Const.NUM_ACTIVE_OCR, binf=50, sliced=True)
        return (int(s[0]), int(s[2]))

    @staticmethod
    def list_active() -> List[bool]:
        """Lists all currently active beards."""
        Navigation.menu("beard")
        Misc.waste_click()
        Inputs.click(*BeardsOfPower.Const.BEARD_LIST_DROPDOWN)

        l_active = [None] * 8
        for i in range(1,8):
            if Processing.check_pixel_color(
                BeardsOfPower.Const.BEARD_LIST_FIRST.x,
                BeardsOfPower.Const.BEARD_LIST_FIRST.y + (i-1) * BeardsOfPower.Const.BEARD_LIST_Y_OFFSET,
                Color((50,50,50)).hex()
            ):
                l_active[i] = True
            else:
                l_active[i] = False

        return l_active

class Questing:
    class State:
        """This class holds a state of Questing.
        This consists of an 'active' flag, a 'major' flag and a 'zone' number.
        """
        def __init__(self, active :bool, major :bool =False, zone :int =0):
            self.active = active
            self.major = major
            self.zone = zone

    inventory_cleaned = False
    
    @staticmethod
    def start_complete() -> None:
        """This starts a new quest if no quest is running.
        If a quest is running, it tries to turn it in.
        """
        Navigation.menu("questing")
        Inputs.click(*coords.QUESTING_START_QUEST)
    
    @staticmethod
    def skip() -> None:
        """This skips your current quest."""
        Navigation.menu("questing")
        time.sleep(userset.MEDIUM_SLEEP)
        Inputs.click(*coords.QUESTING_SKIP_QUEST)
        Navigation.confirm()
    
    @staticmethod
    def get_quest_text() -> str:
        """Check if we have an active quest or not."""
        Navigation.menu("questing")
        Misc.waste_click()  # move tooltip
        time.sleep(userset.SHORT_SLEEP)
        text = Processing.ocr(*coords.OCR_QUESTING_LEFT_TEXT)
        return Processing.one_line(text)
    
    @staticmethod
    def get_available_majors() -> int:
        """Return the amount of available major quests."""
        Navigation.menu("questing")
        text = Processing.ocr(*coords.OCR_QUESTING_MAJORS)
        try:
            match = re.search(r"(\d+)\/\d+", text)
            if match:
                return int(match.group(1))
        except ValueError:
            print("couldn't get current major quests available")
            return -1
    
    @staticmethod
    def get_quest_zone() -> int:
        """Gets current quest zone."""
        text = Questing.get_quest_text().lower()
        for zonename, zone in const.QUEST_ZONE_MAP.items():
            if zonename in text: return zone
        return 0

    @staticmethod
    def get_state() -> Questing.State:
        """Gets the quest state: If there's an active quest, if it's major and its zone."""
        state = Questing.State(active=False)

        text = Questing.get_quest_text().lower()
        if "fetch" in text:
            state.active = True
            if "major quest" in text: state.major = True
            state.zone = Questing.get_quest_zone()
        
        return state
    
    @staticmethod
    def is_using_majors() -> bool:
        """This returns whether the "Use Major Quests if Available" checkbox is toggled ON."""
        return Processing.check_pixel_color(*coords.COLOR_QUESTING_USE_MAJOR)
    
    @staticmethod
    def set_idle(set :bool =True) -> None:
        """Activates or deactivates idle questing."""
        Navigation.menu("questing")
        if Processing.check_pixel_color(*coords.QUESTING_IDLE_INACTIVE) == set:
            Inputs.click(*coords.QUESTING_SUBCONTRACT)
    
    @staticmethod
    def toggle_use_majors() -> None:
        """This toggles ON/OFF the "Use Major Quests if Available" checkbox."""
        Navigation.menu("questing")
        Inputs.click(*coords.QUESTING_USE_MAJOR)
    
    @staticmethod
    def set_use_majors(set :bool =True) -> None:
        """This enables/disables the "Use Major Quests if Available" checkbox.
        
        Args:
	        set: If True, enable the checkbox. If False, disable it.
        """
        Navigation.menu("questing")
        if Questing.is_using_majors() != set:  # Toggle if only one is True
            Questing.toggle_use_majors()

    @staticmethod
    def consume_items(cleanup :bool =False) -> None:
        """Check for items in inventory that can be turned in."""
        Navigation.menu("inventory")
        Inputs.click(*coords.INVENTORY_PAGE[0])
        bmp = Inputs.get_bitmap()
        for item in coords.QUESTING_FILENAMES:
            path = Processing.get_file_path("images", item)
            loc = Processing.image_search(Window.x, Window.y, Window.x + 960, Window.y + 600, path, 0.91, bmp=bmp)
            if loc:
                Inputs.click(*loc, Inputs.Const.MOUSE_RIGHT)
                if cleanup:
                    Inputs.send_string("d")
                    Inputs.ctrl_click(*loc)
                time.sleep(3)  # Need to wait for tooltip to disappear after consuming
    
    @staticmethod
    def start_major(*, idle :bool =False, butter :bool =False) -> bool:
        """Starts a major quest. Cancels any running minor quest.
        
        Args:
	        idle: Set idle questing mode (not default).
        
        Returns:
            Returns False if there's no majors available.
        """
        if Questing.get_available_majors() == 0: return False

        state = Questing.get_state()
        Questing.set_idle(idle)

        if state.active and not state.major: Questing.skip()
        if state.active and state.major: return True
        if butter: Inputs.click(*coords.QUESTING_BUTTER)

        Questing.set_use_majors(True)
        Questing.start_complete()

        return True

    @staticmethod
    def start_minor(*, idle :bool =True, zone :int =0) -> bool:
        """Starts a minor quest. Cancels any running minor quest from a different zone.
        
        Args:
	        idle: Set idle questing mode (default).
	        zone: Set the zone on which you want to quest. Set to zero (default) to quest on any zone.
        
        Returns:
            Returns False if the target quest area is unknown, unrecognized or there's a major currently running.
        """
        state = Questing.get_state()

        # Trying to start minor quest when major is running
        if state.major: return False
        # Trying to quest in non-quest zone
        if zone not in const.QUEST_ZONE_MAP.keys(): return False

        Questing.set_idle(idle)

        # Zone is unspecified
        if zone == 0: 
            if not state.active:
                Questing.set_use_majors(False)
                Questing.start_complete()
            return True

        # Minor running in desired zone
        if zone == state.zone: return True
                
        Questing.set_use_majors(False)
        Questing.start_complete()
        state = Questing.get_state()
        while not state.zone == zone:
            Questing.skip()
            Questing.start_complete()
            state = Questing.get_state()
        
        return True

    @staticmethod
    @deprecated
    def questing(duration :int =30, major :bool =False, subcontract :bool =False, force :int =0, adv_duration :int =2, butter :bool =False) -> None:
        """Procedure for questing.
        
        ===== IMPORTANT =====
        This method uses imagesearch to find items in your inventory, it will
        both right click and ctrl-click items (quick delete keybind), so make
        sure all items are protected.
        
        The method will only check the inventory page that is currently open,
        so make sure it's set to page 1 and that your inventory has space.
        
        If your inventory fills with mcguffins/other drops while it runs, it
        will get stuck doing the same quest forever. Make sure you will have
        space for the entire duration you will leave it running unattended.
        =====================
        
        Args:
	        duration    : The duration in minutes to run if manual mode is selected. If
                        quest gets completed, function will return prematurely.
	        major       : Set to true if you only wish to manually do main quests,
                        if False it will manually do all quests.
	        subcontract : Set to True if you wish to subcontract all quests.
	        force       : Only quest in this zone. This will skip quests until you
                        recieve one for the selected zone, so make sure you disable
                        "Use major quests if available".
	        adv_duration: The time in minutes to spend sniping before checking inventory.
                        A higher value is good when forcing, because you spend less time
                        scanning the inventory and you will not waste any extra quest items.
                        A value around 2 minutes is good when doing majors because it's very
                        likely that the extra items are lost.
        
        Suggested usages:
        questing(major=True)
        questing(subcontract=True)
        If you only wish to manually do major quests (so you can do ITOPOD)
        then I suggest that you only call questing() every 10-15 minutes because
        subcontracting takes very long to finish. Same obviously goes for subcontracting
        only.
        Remember the default duration is 40, which is there to safeguard if something
        goes wrong to break out of the function. Set this higher/lower after your own
        preferences.
        questing(duration=40)
        This will manually complete any quest you get for 30 minutes, then it returns,
        or it returns when the quest is completed.
        Use this together with harvesting ygg, recapping diggers and so on, or even
        sniping ITOPOD.
        """
        end = time.time() + duration * 60
        text = Questing.get_quest_text()
        
        if coords.QUESTING_QUEST_COMPLETE in text.lower():
            Questing.start_complete()
            time.sleep(userset.LONG_SLEEP * 2)
            text = Questing.get_quest_text()  # fetch new quest text
        
        if coords.QUESTING_NO_QUEST_ACTIVE in text.lower():  # if we have no active quest, start one
            Questing.start_complete()
            if force and not Questing.inventory_cleaned:
                Questing.consume_items(True)  # we have to clean up the inventory from any old quest items
                Questing.inventory_cleaned = True
            elif not force:
                Questing.consume_items(True)
            Inputs.click(960, 600)  # move tooltip
            time.sleep(userset.LONG_SLEEP)
            text = Questing.get_quest_text()  # fetch new quest text
        
        if force:
            Questing.set_use_majors(False)
            
            while not coords.QUESTING_ZONES[force] in text.lower():
                Questing.skip()
                Questing.start_complete()
                text = Questing.get_quest_text()
        
        if subcontract:
            if Processing.check_pixel_color(*coords.QUESTING_IDLE_INACTIVE):
                Inputs.click(*coords.QUESTING_SUBCONTRACT)
            return
        
        if major and coords.QUESTING_MINOR_QUEST in text.lower():  # check if current quest is minor
            if Processing.check_pixel_color(*coords.QUESTING_IDLE_INACTIVE):
                Inputs.click(*coords.QUESTING_SUBCONTRACT)
            return
        
        if not Processing.check_pixel_color(*coords.QUESTING_IDLE_INACTIVE):  # turn off idle
            Inputs.click(*coords.QUESTING_SUBCONTRACT)
        if butter:
            Inputs.click(*coords.QUESTING_BUTTER)
        
        for zonename, zone in const.QUEST_ZONE_MAP.items():
            if zonename in text.lower():
                current_time = time.time()
                while current_time < end:
                    if current_time + adv_duration * 60 > end:  # adjust adv_duration if it will cause duration to be exceeded
                        adv_duration = (end - current_time) / 60
                        if adv_duration < 0.5:
                            adv_duration = 0
                            return
                    
                    Adventure.set_zone(zone)
                    Adventure.set_idle(False)
                    Adventure.snipe(adv_duration * 60, regular=True)
                    Adventure.set_idle(True)

                    Inventory.boost_cube()
                    Questing.consume_items()

                    text = Questing.get_quest_text()
                    current_time = time.time()
                    if coords.QUESTING_QUEST_COMPLETE in text.lower():
                        try:
                            start_qp = int(Processing.remove_letters(Processing.ocr(*coords.OCR_QUESTING_QP)))
                        except ValueError:
                            print("Couldn't fetch current QP")
                            start_qp = 0
                        Questing.start_complete()
                        Inputs.click(605, 510)  # move tooltip
                        try:
                            current_qp = int(Processing.remove_letters(Processing.ocr(*coords.OCR_QUESTING_QP)))
                        except ValueError:
                            print("Couldn't fetch current QP")
                            current_qp = 0
                        
                        gained_qp = current_qp - start_qp
                        print(f"Completed quest in zone #{zone} at {datetime.datetime.now().strftime('%H:%M:%S')} for {gained_qp} QP")
                        
                        return
    
    @staticmethod
    def manual(duration :int =30, *, adv_duration :int =120) -> None:
        """Procedure for manual questing.
        
        Args:
	        duration: The duration in MINUTES to run if manual mode is selected. If
                    quest gets completed, function will return prematurely.
	        adv_duration: The time in SECONDS to spend sniping before checking inventory.
                    A higher value is good when forcing, because you spend less time
                    scanning the inventory and you will not waste any extra quest items.
                    A value around 2 minutes is good when doing majors because it's very
                    likely that the extra items are lost.
        
        Warning:
            This method uses imagesearch to find items in your inventory, it will
            both right click and ctrl-click items (quick delete keybind), so make
            sure all items are protected.
            
            The method will only check the inventory page that is currently open,
            so make sure it's set to page 1 and that your inventory has space.
            
            If your inventory fills with mcguffins/other drops while it runs, it
            will get stuck doing the same quest forever. Make sure you will have
            space for the entire duration you will leave it running unattended.
        """
        state = Questing.get_state()
        
        if not state.active:
            raise RuntimeWarning("Ran Questing.manual() with no quest active.")
            return

        end = time.time() + duration * 60
        Adventure.set_zone(state.zone)

        c_time = time.time()
        while c_time < end:
            if c_time + adv_duration > end: adv_duration = end - c_time
            Adventure.set_idle(False)
            Adventure.snipe(adv_duration, regular=True)
            Adventure.set_idle(True)

            Inventory.boost_cube()
            Questing.consume_items()
                    
            text = Processing.one_line(Questing.get_quest_text())
            
            if coords.QUESTING_QUEST_COMPLETE in text.lower():
                try:
                    start_qp = int(Processing.remove_letters(Processing.ocr(*coords.OCR_QUESTING_QP)))
                except ValueError:
                    raise RuntimeWarning("Couldn't fetch current QP")
                    start_qp = 0

                Questing.start_complete()
                Misc.waste_click()

                try:
                    current_qp = int(Processing.remove_letters(Processing.ocr(*coords.OCR_QUESTING_QP)))
                except ValueError:
                    raise RuntimeWarning("Couldn't fetch current QP")
                    current_qp = 0
                
                gained_qp = current_qp - start_qp
                print(f"Completed quest in zone #{state.zone} at {datetime.datetime.now().strftime('%H:%M:%S')} for {gained_qp} QP")
                return
            
            c_time = time.time()

class Hacks:
    @staticmethod
    def activate(targets :List[int] =None, value :int =1e12) -> None:
        """Activate hacks.
        
        Args:
	        targets: List of hacks to level up. Default value is [1, 2, 3, 4, 5, 6, 7, 8].
	        value  : Resource to spend, default to 1e12.
        """
        targets = targets or []
        Misc.set_input(value // len(targets))
        Navigation.menu("hacks")
        for i in targets:
            page = ((i - 1) // 8)
            item = i - (page * 8)
            Inputs.click(*coords.HACK_PAGE[page])
            Inputs.click(*coords.HACKS[item])

class Wishes:
    completed_wishes = []
