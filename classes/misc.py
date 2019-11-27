"""Handles various miscellaneous things, but mostly resources and rebirths."""

import time
import re

from collections import namedtuple
from PIL.Image   import Image as PIL_Image
from typing      import List, Tuple

from classes.inputs     import Inputs
from classes.navigation import Navigation
from classes.processing import Processing
from classes.window     import Window

import coordinates  as coords
import usersettings as userset


class Misc:
    @staticmethod
    def reclaim_all() -> None:
        """Reclaim all resources from all features."""
        Inputs.send_string("r")
        Inputs.send_string("t")
        Inputs.send_string("f")
    
    @staticmethod
    def reclaim_res(energy :bool =False, magic :bool =False, r3 :bool =False) -> None:
        """Reclaim resources of choosing from all features.
        
        Keyword arguments
        energy -- If True, reclaim energy.
        magic  -- If True, reclaim magic.
        r3     -- If True, reclaim resource 3.
        """
        if energy:
            Inputs.send_string("r")
        if magic:
            Inputs.send_string("t")
        if r3:
            Inputs.send_string("f")
    
    @staticmethod
    def reclaim_bm() -> None:
        """Remove all magic from BM."""
        Navigation.menu("bloodmagic")
        Misc.set_input(coords.INPUT_MAX)
        for coord in coords.BM_RECLAIM:
            Inputs.click(*coord)
    
    @staticmethod
    def reclaim_ngu(magic :bool =False) -> None:
        """Remove all e/m from NGUs."""
        if magic:
            Navigation.ngu_magic()
        else:
            Navigation.menu("ngu")
        Misc.set_input(coords.INPUT_MAX)
        for i in range(1, 10):
            NGU = coords.Pixel(coords.NGU_MINUS.x, coords.NGU_PLUS.y + i * 35)
            Inputs.click(*NGU)
    
    @staticmethod
    def reclaim_tm(energy :bool =True, magic :bool =False) -> None:
        """Remove all e/m from TM.
        
        Keyword arguments
        energy -- If True, reclaim energy from TM.
        magic  -- If True, reclaim magic from TM.
        """
        Navigation.menu("timemachine")
        Misc.set_input(coords.INPUT_MAX)
        if magic:
            Inputs.click(*coords.TM_MULT_MINUS)
        if energy:
            Inputs.click(*coords.TM_SPEED_MINUS)
    
    @staticmethod
    def reclaim_aug() -> None:
        """Remove all energy from augs"""
        Navigation.menu("augmentations")
        Misc.set_input(coords.INPUT_MAX)
        Inputs.click(*coords.AUG_SCROLL_TOP)
        scroll_down = False
        for i, k in enumerate(coords.AUGMENT.keys()):
            if i >= 10 and not scroll_down:
                Inputs.click(*coords.AUG_SCROLL_BOT)
                Inputs.click(*coords.AUG_SCROLL_BOT)
                time.sleep(1)
                scroll_down = True
            Inputs.click(coords.AUG_MINUS_X, coords.AUGMENT[k].y)
    
    @staticmethod
    def save_check() -> None:
        """Check if we can do the daily save for AP.
        Make sure no window in your browser pops up when you click the "Save"
        button, otherwise sit will mess with the rest of the script.
        """
        if Processing.check_pixel_color(*coords.IS_SAVE_READY):
            Inputs.click(*coords.SAVE)
        return
    
    # crops the misc breakdown image, cutting off empty space on the right
    @staticmethod
    def __cutoff_right(bmp) -> PIL_Image:
        first_pix = bmp.getpixel((0, 0))
        width, height = bmp.size
        
        count = 0
        for x in range(8, width):
            dif = False
            for y in range(0, height):
                if not first_pix == bmp.getpixel((x, y)):
                    dif = True
                    break
            
            if dif: count = 0
            else:
                count += 1
                if count > 8:
                    return bmp.crop((0, 0, x , height))
        
        return bmp
    
    # splits the three parts of the resource breakdown (pow, bars, cap)
    @staticmethod
    def __split_breakdown(bmp) -> List[PIL_Image]:
        first_pix = bmp.getpixel((0, 0))
        width, height = bmp.size
        y1 = 1
        offset_x = coords.OCR_BREAKDOWN_NUM[0] - coords.OCR_BREAKDOWN_COLONS[0]
        
        slices = []
        for _ in range(0, 3):
            for y in range(y1, height):
                if not first_pix == bmp.getpixel((0, y)):
                    y0 = y
                    break
            
            for y in range(y0, height, coords.BREAKDOWN_OFFSET_Y):
                if first_pix == bmp.getpixel((0, y)):
                    y1 = y
                    break
            
            s = bmp.crop((offset_x, y0 - 8, width, y1))
            slices.append(Misc.__cutoff_right(s))
        
        return slices
    
    # Goes to stats breakdown, makes a screenshot
    # Gets it split into three containing all the numbers by calling __split_breakdown
    # Sends all thre images to OCR
    # Returns a list of lists of the numbers from stats breakdown
    @staticmethod
    def __get_res_breakdown(resource, ocrDebug=False, bmp=None, debug=False) -> List[List[str]]:
        Navigation.stat_breakdown()
        
        if   resource == 1: Inputs.click(*coords.BREAKDOWN_E)
        elif resource == 2: Inputs.click(*coords.BREAKDOWN_M)
        elif resource == 3: Inputs.click(*coords.BREAKDOWN_R)
        else : raise RuntimeError("Invalid resource")
        
        if bmp is None:
            bmp = Inputs.get_cropped_bitmap(*Window.gameCoords(*coords.OCR_BREAKDOWN_COLONS))
        if debug: bmp.show()

        imgs = Misc.__split_breakdown(bmp)
        
        ress = []
        for img in imgs:
            if debug: img.show()
            s = Processing.ocr(0, 0, 0, 0, bmp=img, debug=ocrDebug, binf=220, sliced=True)
            s = s.splitlines()
            s2 = [x for x in s if x != ""]  # remove empty lines
            ress.append(s2)
        
        return ress
    
    # Gets the numbers on stats breakdown for the resource and value passed
    # val = 0 for power, 1 for bars and 2 for cap
    @staticmethod
    def __get_res_val(resource, val) -> int:
        s = Misc.__get_res_breakdown(resource)[val][-1]
        return Processing.get_numbers(s)[0]
    
    @staticmethod
    def get_pow(resource :int) -> int:
        """Get the power for energy, magic, or resource 3.
        
        Keyword arguments
        resource -- The resource to get power for. 1 for energy, 2 for magic and 3 for r3.
        """
        return Misc.__get_res_val(resource, 0)
    
    @staticmethod
    def get_bars(resource :int) -> int:
        """Get the bars for energy, magic, or resource 3.
        
        Keyword arguments
        resource -- The resource to get bars for. 1 for energy, 2 for magic and 3 for r3.
        """
        return Misc.__get_res_val(resource, 1)
    
    @staticmethod
    def get_cap(resource :int) -> int:
        """Get the cap for energy, magic, or resource 3.
        
        Keyword arguments
        resource -- The resource to get cap for. 1 for energy, 2 for magic and 3 for r3.
        """
        return Misc.__get_res_val(resource, 2)
    
    @staticmethod
    def get_idle_cap(resource :int) -> int:
        """Get the available idle energy, magic, or resource 3.
        
        Keyword arguments
        resource -- The resource to get idle cap for. 1 for energy, 2 for magic and 3 for r3.
        """
        try:  # The sliced argument was meant for low values with get_pow/bars/cap
            # But also serves for low idle caps
            if   resource == 1: res = Processing.ocr(*coords.OCR_ENERGY, sliced=True)
            elif resource == 2: res = Processing.ocr(*coords.OCR_MAGIC , sliced=True)
            elif resource == 3: res = Processing.ocr(*coords.OCR_R3    , sliced=True)
            else : raise RuntimeError("Invalid resource")
            
            res = Processing.get_numbers(res)[0]
            return res
            
        except IndexError:
            print("couldn't get idle cap")
            return 0

    @staticmethod
    def set_input(value :int) -> None:
        """Sets a value in the input box.
        Requires the current menu to have an imput box.
        
        Keyword arguments
        value -- The value to be set
        """
        Navigation.input_box()
        Inputs.send_string(value)
        Misc.waste_click()
    
    @staticmethod
    def waste_click() -> None:
        """Make a click that does nothing"""
        Inputs.click(*coords.WASTE_CLICK)
        time.sleep(userset.FAST_SLEEP)

class Rebirth:
    @staticmethod
    def rebirth() -> None:
        """Start a rebirth or challenge."""
        Navigation.menu("fight")
        Inputs.click(*coords.FIGHT_STOP)
        Navigation.rebirth()
        Inputs.click(*coords.REBIRTH)
        Inputs.click(*coords.REBIRTH_BUTTON)
        Inputs.click(*coords.CONFIRM)
    
    @staticmethod
    def check_challenge(getNum :bool =False) -> int:
        """Check if a challenge is active.
        
        Keyword arguments
        getNum. -- If true, return the number of the active challenge.
                   This is slower.
                   If False or omitted, return if a challenge is active.
        """
        Navigation.rebirth()
        Inputs.click(*coords.CHALLENGE_BUTTON)
        time.sleep(userset.LONG_SLEEP)
        active = Processing.check_pixel_color(*coords.COLOR_CHALLENGE_ACTIVE)
        
        if not active:
            return False
        if not getNum:
            return True
        
        text = Processing.ocr(*coords.OCR_CHALLENGE_NAME)
        if   "basic"        in text.lower(): return 1
        elif "augs"         in text.lower(): return 2
        elif "24 hour"      in text.lower(): return 3
        elif "100 level"    in text.lower(): return 4
        elif "equipment"    in text.lower(): return 5
        elif "troll"        in text.lower(): return 6
        elif "rebirth"      in text.lower(): return 7
        elif "laser"        in text.lower(): return 8
        elif "blind"        in text.lower(): return 9
        elif "ngu"          in text.lower(): return 10
        elif "time machine" in text.lower(): return 11
        else:                                return -1
    
    @staticmethod
    def time_() -> Tuple[int, time.struct_time]:
        """Get the current rebirth time.
        returns a namedtuple(days, timestamp) where days is the number
        of days displayed in the rebirth time text and timestamp is a
        time.struct_time object.
        """
        Rebirth_time = namedtuple('Rebirth_time', 'days timestamp')
        t = Processing.ocr(*coords.OCR_REBIRTH_TIME)
        x = re.search(r"((?P<days>[0-9]+) days? )?((?P<hours>[0-9]+):)?(?P<minutes>[0-9]+):(?P<seconds>[0-9]+)", t)
        days = 0
        if x is None:
            timestamp = time.strptime("0:0:0", "%H:%M:%S")
        else:
            if x.group('days') is None:
                days = 0
            else:
                days = int(x.group('days'))
            
            if x.group('hours') is None:
                hours = "0"
            else:
                hours = x.group('hours')
            
            if x.group('minutes') is None:
                minutes = "0"
            else:
                minutes = x.group('minutes')
            
            if x.group('seconds') is None:
                seconds = "0"
            else:
                seconds = x.group('seconds')
            timestamp = time.strptime(f"{hours}:{minutes}:{seconds}", "%H:%M:%S")
        return Rebirth_time(days, timestamp)
    
    @staticmethod
    def time_seconds() -> int:
        """Get the Rebirth time in seconds"""
        rt = Rebirth.time_()
        seconds = ((rt.days * 24 + rt.timestamp.tm_hour) * 60 + rt.timestamp.tm_min) * 60 + rt.timestamp.tm_sec
        return seconds
