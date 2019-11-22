"""Handles different challenges"""

import time
from typing import List

import coordinates as coords
import usersettings as userset
from classes.discord import Discord
from classes.features import BloodMagic, Rebirth
from classes.inputs import Inputs
from classes.navigation import Navigation
from classes.processing import Processing
from classes.window import Window

from .challenges.augment     import augment
from .challenges.basic       import basic
from .challenges.blind       import blind
from .challenges.equipment   import equipment
from .challenges.laser       import laser
from .challenges.level       import level
from .challenges.ngu         import ngu
from .challenges.rebirth     import rebirth
from .challenges.timemachine import timemachine


class ChInfo:
    """Holds info about a challenge, including which script to run"""
    def __init__(self, name="", script=None, extra=[]):
        self.name = name
        self.script = script
        self.extra = extra

def init(ch_list):
    """PyLint wants a docstring. So this is a docstring"""
    def get24boss():
        try:
            x = coords.CHALLENGE.x
            y = coords.CHALLENGE.y + 3 * coords.CHALLENGEOFFSET

            Navigation.challenges()
            Inputs.click(x, y, button="right")
            time.sleep(userset.LONG_SLEEP)
            target = Processing.ocr(*coords.OCR_CHALLENGE_24HC_TARGET)
            target = Processing.get_numbers(target)[0]
            return f"Target boss: {target}"
        except ValueError:
            Discord.send_message("Couldn't detect the target level of 24HC", Discord.ERROR)
            return "Couldn't detect the target level of 24HC"

    ch_list.append(ChInfo("Basic", basic))
    ch_list.append(ChInfo("No Augments", augment))
    ch_list.append(ChInfo("24h", basic, [get24boss]))
    ch_list.append(ChInfo("100 Level", level, [
        "IMPORTANT",
        "Set target level for energy buster to 67 and charge shot to 33.",
        "Disable 'Advance Energy' in Augmentation",
        "Disable beards if you cap ultra fast."
    ]))
    ch_list.append(ChInfo("No Equipment", equipment))
    ch_list.append(ChInfo("Troll", Window.shake, ["Do it yourself, fam."]))
    ch_list.append(ChInfo("No Rebirth", rebirth))
    ch_list.append(ChInfo("Laser Sword", laser, [
        "LSC doesn't reset your number, make sure your number is high enough to make laser swords."
    ]))
    ch_list.append(ChInfo("Blind", blind))
    ch_list.append(ChInfo("No NGU", ngu))
    ch_list.append(ChInfo("No Time Machine", timemachine))

Ch_List = []
init(Ch_List)

class Challenge:
    """Handles different challenges."""
    
    @staticmethod
    def run_challenge(challenge :int, cont :bool =False) -> None:
        """Run the selected challenge.
        
        Keyword arguments
        challenge -- The index of the challenge, starting at 1 for Basic challenge,
                     ending at 11 for No TM challenge
        cont      -- Whether the challenge is already running.
        """
        global Ch_List
        Navigation.challenges()
        
        if cont: pass
        else:
            x = coords.CHALLENGE.x
            y = coords.CHALLENGE.y + challenge * coords.CHALLENGEOFFSET
            Inputs.click(x, y)
            time.sleep(userset.LONG_SLEEP)
            Navigation.confirm()
        
        chall = Ch_List[challenge-1]
        print(f"Starting {chall.name} Challenge script.")
        for x in chall.extra:
            if callable(x): print(x())
            else: print(x)
        chall.script()
    
    @staticmethod
    def start_challenge(challenge :int, quitCurrent :bool =False) -> None:
        """Start the selected challenge. Checks for currently running challenges.
        
        Keyword arguments
        challenge   -- The index of the challenge, starting at 1 for Basic challenge,
                       ending at 11 for No TM challenge
        quitCurrent -- Quit the current challenge if it is different to the desired.
        """
        BloodMagic.toggle_auto_spells(drop=False)
        
        chall = Rebirth.check_challenge(getNum=True)
        if chall and chall != challenge:
            print(f"A challenge is currently running ({chall}).")
            if quitCurrent:
                print("Quitting current challenge.")
                Navigation.challenge_quit()
            else: Challenge.run_challenge(chall, cont=True)

        Challenge.run_challenge(challenge)
    
    @staticmethod
    def list() -> List[str]:
        """Return the list of challenge names with their corresponding number.
        """
        global Ch_List
        
        l = []
        for i in range(len(Ch_List)):
            if i < 9: l.append(f"{i+1}  {Ch_List[i].name}")
            else:     l.append(f"{i+1} {Ch_List[i].name}")
        return l
