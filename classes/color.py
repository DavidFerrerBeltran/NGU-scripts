from __future__ import annotations

from typing import Tuple

class Color:
    # Do not use Color(rgb, hex) to initialize a Color object
    # Use RGB(r) or hex(h) instead
    def __init__(self :Color, rgb :Tuple[int, int, int], hex :str) -> None:
        self.rgb = rgb
        self.hex = hex
        
    def __eq__(a :Color, b :Color) -> bool:
        return a.rgb == b.rgb
    
    def __str__(self :Color) -> str:
        return self.hex
    
    @staticmethod
    def RGB(r :Tuple[int, int, int]) -> Color:
        return Color(r, Color.rgb_to_hex(r))
        
    @staticmethod
    def hex(h :str) -> Color:
        return Color(Color.hex_to_rgb(h), h)
        
    def get_RGB(self :Color) -> Tuple[int, int, int]:
        return self.rgb
    
    def get_hex(self :Color) -> str:
        return self.hex
    
    @staticmethod
    def rgb_to_hex(tup :Tuple[int, int, int]) -> str:
        """Convert RGB value to hex."""
        return '%02x%02x%02x'.upper() % (tup[0], tup[1], tup[2])

    @staticmethod
    def hex_to_rgb(str :str) -> Tuple[int, int, int]:
        """Convert hex value to RGB."""
        return tuple(int(str[i:i + 2], 16) for i in (0, 2, 4))
