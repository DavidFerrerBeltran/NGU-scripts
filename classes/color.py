from __future__ import annotations

from typing import Tuple

RGB_color = Tuple[int, int, int]
hex_color = str

class Color:
    # Do not use Color(rgb, hex) to initialize a Color object
    # Use RGB(r) or hex(h) instead
    def __init__(self :Color, r :RGB_color, h :hex_color) -> None:
        self.r = r
        self.h = h

    # pylint: disable=E0213
    def __eq__(a :Color, b :Color) -> bool:
        return a.r == b.r
    
    def __str__(self :Color) -> str:
        return self.h
    
    @staticmethod
    def RGB(r :RGB_color) -> Color:
        return Color(r, Color.rgb_to_hex(r))
        
    @staticmethod
    def hex(h :hex_color) -> Color:
        return Color(Color.hex_to_rgb(h), h)
        
    def get_RGB(self :Color) -> RGB_color:
        return self.r
    
    def get_hex(self :Color) -> hex_color:
        return self.h
    
    @staticmethod
    def rgb_to_hex(tup :RGB_color) -> hex_color:
        """Convert RGB value to hex."""
        return '%02x%02x%02x'.upper() % (tup[0], tup[1], tup[2])

    @staticmethod
    def hex_to_rgb(string :hex_color) -> RGB_color:
        """Convert hex value to RGB."""
        return tuple(int(string[i:i + 2], 16) for i in (0, 2, 4))
