import datetime
import os
import re

from typing import Iterable, List, Optional, Tuple, Union

from PIL       import Image as image # image module
from PIL.Image import Image as PIL_Image # image.image class
from PIL import ImageFilter
import cv2
import numpy

import pytesseract

from classes.window import Window
from classes.inputs import Inputs
from classes.color  import Color, RGB_color

Coordinates = Tuple[int, int]

class Processing:
    @staticmethod
    def pixel_search(color :Color, x_start :int, y_start :int, x_end :int, y_end :int) -> Optional[Coordinates]:
        """Find the first pixel with the supplied color within area.
        
        Function searches per row, left to right. Returns the coordinates of
        first match or None, if nothing is found.
        """
        bmp = Inputs.get_bitmap()
        width, height = bmp.size
        
        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                if y > height or x > width:
                    continue
                pix_color = bmp.getpixel((x, y))
                if pix_color == color.get_RGB():
                    return x - 8, y - 8
        
        return None

    @staticmethod
    def image_search(x_start :int, y_start :int, x_end :int, y_end :int,
                     img :str, threshold :int, bmp :PIL_Image =None) -> Optional[Coordinates]:
        """Search the screen for the supplied picture.
        
        Returns a tuple with x,y-coordinates, or None if result is below
        the threshold.
        
        Keyword arguments:
        image     -- Filename or path to file that you search for.
        threshold -- The level of fuzziness to use - a perfect match will be
                     close to 1, but probably never 1. In my testing use a
                     value between 0.7-0.95 depending on how strict you wish
                     to be.
        bmp       -- a bitmap from the get_bitmap() function, use this if you're
                     performing multiple different OCR-readings in succession
                     from the same page. This is to avoid to needlessly get the
                     same bitmap multiple times. If a bitmap is not passed, the
                     function will get the bitmap itself. (default None)
        """
        if not bmp: bmp = Inputs.get_bitmap()
        # Bitmaps are created with a 8px border
        search_area = bmp.crop((x_start + 8, y_start + 8,
                                x_end + 8, y_end + 8))
        search_area = numpy.asarray(search_area)
        search_area = cv2.cvtColor(search_area, cv2.COLOR_RGB2GRAY)
        template = cv2.imread(img, 0)
        res = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val < threshold:
            return None
        
        return max_loc

    @staticmethod
    def find_all(
        x_start :int,
        y_start :int,
        x_end :int,
        y_end :int,
        img :str,
        threshold: float,
        bmp :PIL_Image =None) -> Optional[List[Coordinates]]:
        """Search the screen for the supplied picture.
        
        Returns a list with x, y-coordinates with all matches, or None if result is below
        the threshold.
        
        Keyword arguments:
        image     -- Filename or path to file that you search for.
        threshold -- The level of fuzziness to use - a perfect match will be
                     close to 1, but probably never 1. In my testing use a
                     value between 0.7-0.95 depending on how strict you wish
                     to be.
        bmp       -- a bitmap from the get_bitmap() function, use this if you're
                     performing multiple different OCR-readings in succession
                     from the same page. This is to avoid to needlessly get the
                     same bitmap multiple times. If a bitmap is not passed, the
                     function will get the bitmap itself. (default None)
        """
        if not bmp: bmp = Inputs.get_bitmap()
        # Bitmaps are created with a 8px border
        search_area = bmp.crop((x_start + 8, y_start + 8,
                                x_end + 8, y_end + 8))
        search_area = numpy.asarray(search_area)
        search_area = cv2.cvtColor(search_area, cv2.COLOR_RGB2GRAY)
        template = cv2.imread(img, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
        locs = numpy.where(res >= threshold)
        lst = []
        for loc in zip(*locs[::-1]):
            lst.append((loc[0] + w // 2, loc[1] + h // 2))
        return lst

    @staticmethod
    def rgb_equal(a :RGB_color, b :RGB_color) -> bool:
        return a == b # Tuples are this easy to compare
    
    @staticmethod
    def ocr(
         x_start :int,
         y_start :int,
         x_end :int,
         y_end :int,
         debug :bool =False,
         bmp :PIL_Image =None,
         cropb :bool =False,
         filter :bool =True,
         binf :int =0,
         sliced :bool =False
     ) -> str:
        """Perform an OCR of the supplied area, returns a string of the result.
        
        Keyword arguments
        debug  -- Saves an image of what is sent to the OCR (default False)
        bmp    -- A bitmap from the get_bitmap() function, use this if you're
                  performing multiple different OCR-readings in succession from
                  the same page. This is to avoid to needlessly get the same
                  bitmap multiple times. If a bitmap is not passed, the function
                  will get the bitmap itself. (default None)
        cropb  -- Whether the bmp provided should be cropped.
        filter -- Whether to filter the image for better OCR.
        binf   -- Threshold value for binarizing filter. Zero means no filtering.
        sliced -- Whether the image has ben sliced so there's very little blank
                  space. Gets better readings from small values for some reason.
        """
        x_start += Window.x
        x_end   += Window.x
        y_start += Window.y
        y_end   += Window.y

        if bmp is None:
            bmp = Inputs.get_cropped_bitmap(x_start, y_start, x_end, y_end)
        
        elif cropb:
            # Bitmaps are created with a 8px border
            bmp = bmp.crop((x_start + 8, y_start + 8, x_end + 8, y_end + 8))
        
        if binf > 0: # Binarizing Filter
            fn = lambda x : 255 if x > binf else 0
            bmp = bmp.convert('L') # To Monochrome
            bmp = bmp.point(fn, mode='1')
            if debug: bmp.save("debug_ocr_whiten.png")
        
        if filter: # Resizing and sharpening
            *_, right, lower = bmp.getbbox()
            bmp = bmp.resize((right * 4, lower * 4), image.BICUBIC)  # Resize image
            bmp = bmp.filter(ImageFilter.SHARPEN)
            if debug: bmp.save("debug_ocr_filter.png")
            
        if sliced: s = pytesseract.image_to_string(bmp, config='--psm 6')
        else:      s = pytesseract.image_to_string(bmp, config='--psm 4')
        
        return s

    @staticmethod
    def check_pixel_color(x :int, y :int, checks :Union[str, Iterable[str]]) -> bool:
        """Check if coordinate matches with one or more colors."""
        color = Inputs.get_pixel_color(x, y).get_hex()
        if isinstance(checks, list):
            for check in checks:
                if check == color:
                    return True

        return color == checks

    @staticmethod
    def remove_spaces(s :str) -> str:
        """Remove all spaces from string."""
        return "".join(s.split(" "))

    @staticmethod
    def remove_number_separators(s :str) -> str:
        """Remove all separators from number."""
        return "".join(s.split(","))
    
    @staticmethod
    def remove_letters(s :str) -> str:
        """Remove all non digit characters from string."""
        return re.sub('[^0-9]', '', s)

    @staticmethod
    def get_numbers(s :str) -> Iterable[int]:
        """Finds all numbers in a string"""
        s = Processing.remove_spaces(s)
        s = Processing.remove_number_separators(s)
        match = re.findall(r"(\d+(\.\d+E\+\d+)?)", s)
        nums = [int(float(x[0])) for x in match]
        return nums

    @staticmethod
    def get_file_path(directory :str, file :str) -> str:
        """Get the absolute path for a file."""
        working = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(working, directory, file)
        return path

    @staticmethod
    def ocr_number(x_1 :int, y_1 :int, x_2 :int, y_2 :int) -> int:
        """Remove all non-digits."""
        return int(Processing.remove_letters(Processing.ocr(x_1, y_1, x_2, y_2)))

    @staticmethod
    def ocr_notation(x_1 :int, y_1 :int, x_2 :int, y_2 :int) -> int:
        """Convert scientific notation from string to int."""
        return int(float(Processing.ocr(x_1, y_1, x_2, y_2)))

    @staticmethod
    def save_screenshot() -> None:
        """Save a screenshot of the game."""
        bmp = Inputs.get_bitmap()
        bmp = bmp.crop((Window.x + 8, Window.y + 8, Window.x + 968, Window.y + 608))
        if not os.path.exists("screenshots"):
            os.mkdir("screenshots")
        bmp.save('screenshots/' + datetime.datetime.now().strftime('%d-%m-%y-%H-%M-%S') + '.png')
        
