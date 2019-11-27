"""
This handles color data
"""
from __future__ import annotations

from typing import Tuple, Union

RGB_color = Tuple[int, int, int]
hex_color = str

class Color:
    BLACK = None
    WHITE = None

    def __init__(self :Color, col :Union[RGB_color, hex_color]) -> None:
        """Create a color object by either passing a hex or RGB color."""
        if isinstance(col, hex_color):
            self.h = col
            self.r = Color.hex_to_rgb(col)
        elif (
            isinstance(col, tuple) and len(col) == 3 and
            isinstance(col[0], int) and isinstance(col[1], int) and isinstance(col[2], int)
        ):
            self.r = col
            self.h = Color.rgb_to_hex(col)
        else: raise TypeError("called Color(col) with a parameter that's neither hex or RGB.")

    # solves pylint complaining about no self as first argument
    # pylint: disable=E0213
    def __eq__(a :Color, b :Union[Color, RGB_color, hex_color]) -> bool:
        if isinstance(b, Color):
            return a.r == b.r
        else:
            return a == Color(b)
    
    def __str__(self :Color) -> str:
        return self.h
        
    def RGB(self :Color) -> RGB_color:
        """Get color in RGB form"""
        return self.r
    
    def hex(self :Color) -> hex_color:
        """Get color in hex form"""
        return self.h
    
    @staticmethod
    def rgb_to_hex(tup :RGB_color) -> hex_color:
        """Convert RGB value to hex."""
        return '%02x%02x%02x'.upper() % (tup[0], tup[1], tup[2])

    @staticmethod
    def hex_to_rgb(string :hex_color) -> RGB_color:
        """Convert hex value to RGB."""
        return tuple(int(string[i:i + 2], 16) for i in (0, 2, 4))

Color.BLACK = Color("000000")
Color.WHITE = Color("FFFFFF")
