"""Input class contains functions for mouse and keyboard input."""
from ctypes import windll
import win32api
import win32con as wcon
import win32gui
import win32ui

import time

from PIL import Image as image
from PIL.Image import Image as PIL_Image

import usersettings as userset
from classes.window import Window
from classes.color  import Color

class Inputs:
    """This class handles inputs."""
    
    class Const:
        API = None

        MOUSE_LEFT  = 1
        MOUSE_RIGHT = 2

        ARROW_LEFT  = 1
        ARROW_RIGHT = 2
        ARROW_UP    = 3
        ARROW_DOWN  = 4
    
    @staticmethod
    def click(x :int, y :int, button :int =Const.MOUSE_LEFT, *, fast :bool =False) -> None:
        """Click at pixel xy."""
        x += Window.x
        y += Window.y
        lParam = win32api.MAKELONG(x, y)

        # MOUSEMOVE event is required for game to register clicks correctly
        win32gui.PostMessage(Window.id, wcon.WM_MOUSEMOVE, 0, lParam)

        while (win32api.GetKeyState(wcon.VK_CONTROL) < 0 or
               win32api.GetKeyState(wcon.VK_SHIFT) < 0 or
               win32api.GetKeyState(wcon.VK_MENU) < 0):
            time.sleep(0.005)
        
        if   button == Inputs.Const.MOUSE_LEFT:
            win32gui.PostMessage(Window.id, wcon.WM_LBUTTONDOWN, wcon.MK_LBUTTON, lParam)
            win32gui.PostMessage(Window.id, wcon.WM_LBUTTONUP, wcon.MK_LBUTTON, lParam)
        elif button == Inputs.Const.MOUSE_RIGHT:
            win32gui.PostMessage(Window.id, wcon.WM_RBUTTONDOWN, wcon.MK_RBUTTON, lParam)
            win32gui.PostMessage(Window.id, wcon.WM_RBUTTONUP, wcon.MK_RBUTTON, lParam)
        else: raise RuntimeError("Wrong mouse button.")
        
        # Sleep lower than 0.1 might cause issues when clicking in succession
        if fast:
            time.sleep(userset.FAST_SLEEP)
        else:
            time.sleep(userset.MEDIUM_SLEEP)
        
    @staticmethod
    def click_drag(x :int, y :int, x2 :int, y2 :int, button :int =Const.MOUSE_LEFT) -> None:
        """Click at pixel xy."""
        x += Window.x
        y += Window.y
        x2 += Window.x
        y2 += Window.y
        lParam = win32api.MAKELONG(x, y)
        lParam2 = win32api.MAKELONG(x2, y2)

        # MOUSEMOVE event is required for game to register clicks correctly
        win32gui.PostMessage(Window.id, wcon.WM_MOUSEMOVE, 0, lParam)

        while (win32api.GetKeyState(wcon.VK_CONTROL) < 0 or
               win32api.GetKeyState(wcon.VK_SHIFT) < 0 or
               win32api.GetKeyState(wcon.VK_MENU) < 0):
            time.sleep(0.005)
        
        if   button == Inputs.Const.MOUSE_LEFT:
            win32gui.PostMessage(Window.id, wcon.WM_LBUTTONDOWN, wcon.MK_LBUTTON, lParam)
        elif button == Inputs.Const.MOUSE_RIGHT:
            win32gui.PostMessage(Window.id, wcon.WM_RBUTTONDOWN, wcon.MK_LBUTTON, lParam)
        else: raise RuntimeError("Wrong mouse button.")
        
        time.sleep(userset.LONG_SLEEP * 2)
        win32gui.PostMessage(Window.id, wcon.WM_MOUSEMOVE, 0, lParam2)
        time.sleep(userset.SHORT_SLEEP)

        if   button == Inputs.Const.MOUSE_LEFT:
            win32gui.PostMessage(Window.id, wcon.WM_LBUTTONUP, wcon.MK_LBUTTON, lParam2)
        elif button == Inputs.Const.MOUSE_RIGHT:
            win32gui.PostMessage(Window.id, wcon.WM_RBUTTONUP, wcon.MK_LBUTTON, lParam2)
        
        time.sleep(userset.MEDIUM_SLEEP)

    @staticmethod
    def ctrl_click(x :int, y :int, button :int =Const.MOUSE_LEFT) -> None:
        """Clicks at pixel x, y while simulating the CTRL button to be down."""
        x += Window.x
        y += Window.y
        lParam = win32api.MAKELONG(x, y)

        while (win32api.GetKeyState(wcon.VK_CONTROL) < 0 or
               win32api.GetKeyState(wcon.VK_SHIFT) < 0 or
               win32api.GetKeyState(wcon.VK_MENU) < 0):
            time.sleep(0.005)

        win32gui.PostMessage(Window.id, wcon.WM_KEYDOWN, wcon.VK_CONTROL, 0)

        if   button == Inputs.Const.MOUSE_LEFT:
            win32gui.PostMessage(Window.id, wcon.WM_LBUTTONDOWN, wcon.MK_LBUTTON, lParam)
            win32gui.PostMessage(Window.id, wcon.WM_LBUTTONUP, wcon.MK_LBUTTON, lParam)
        elif button == Inputs.Const.MOUSE_RIGHT:
            win32gui.PostMessage(Window.id, wcon.WM_RBUTTONDOWN, wcon.MK_RBUTTON, lParam)
            win32gui.PostMessage(Window.id, wcon.WM_RBUTTONUP, wcon.MK_RBUTTON, lParam)
        else: raise RuntimeError("Wrong mouse button.")

        win32gui.PostMessage(Window.id, wcon.WM_KEYUP, wcon.VK_CONTROL, 0)
        time.sleep(userset.MEDIUM_SLEEP)

    @staticmethod
    def send_arrow(arrow :int) -> None:
        """Sends an arrow key press"""
        if   arrow == Inputs.Const.ARROW_LEFT:  key = wcon.VK_LEFT
        elif arrow == Inputs.Const.ARROW_RIGHT: key = wcon.VK_RIGHT
        elif arrow == Inputs.Const.ARROW_UP:    key = wcon.VK_UP
        elif arrow == Inputs.Const.ARROW_DOWN:  key = wcon.VK_DOWN
        else: raise RuntimeError("Wrong arrow key.")
        
        win32gui.PostMessage(Window.id, wcon.WM_KEYDOWN, key, 0)
        time.sleep(0.05)
        win32gui.PostMessage(Window.id, wcon.WM_KEYUP, key, 0)
        time.sleep(0.05)
    
    @staticmethod
    def send_string(string :str) -> None:
        """Send one or multiple characters to the Window."""
        # Ensure it's a string by converting it to a string
        for c in str(string):
            # Make sure no key modifier is pressed
            while (win32api.GetKeyState(wcon.VK_CONTROL) < 0 or
                   win32api.GetKeyState(wcon.VK_SHIFT)   < 0 or
                   win32api.GetKeyState(wcon.VK_MENU)    < 0):
                time.sleep(0.005)
            
            vkc = win32api.VkKeyScan(c)  # Get virtual key code for character c
            # Only one keyup or keydown event needs to be sent
            win32gui.PostMessage(Window.id, wcon.WM_KEYDOWN, vkc, 0)
    
    @staticmethod
    def get_bitmap(*, debug :bool = False) -> PIL_Image:
        """Get and return a bitmap of the Window."""
        left, top, right, bot = win32gui.GetWindowRect(Window.id)
        w = right - left
        h = bot - top
        hwnd_dc = win32gui.GetWindowDC(Window.id)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(save_bitmap)
        windll.user32.PrintWindow(Window.id, save_dc.GetSafeHdc(), 0)
        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)

        # This creates an Image object from Pillow
        bmp = image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                               bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(Window.id, hwnd_dc)
        
        if debug: bmp.save("asdf.png")
        return bmp

    @staticmethod
    def get_cropped_bitmap(x :int =0, y :int =0, x2 :int =960, y2 :int =600) -> PIL_Image:
        """Get, crop and return a bitmap of the Window."""
        crop_rect = (x + 8, y + 8, x2 + 8, y2 + 8)
        return Inputs.get_bitmap().crop(crop_rect)
    
    @staticmethod
    def get_pixel_color(x :int, y :int, *, debug :bool =False) -> Color:
        """Get the color of selected pixel in HEX."""
        dc = win32gui.GetWindowDC(Window.id)
        rgba = win32gui.GetPixel(dc, x + 8 + Window.x, y + 8 + Window.y)
        win32gui.ReleaseDC(Window.id, dc)
        r = rgba & 0xff
        g = rgba >> 8 & 0xff
        b = rgba >> 16 & 0xff
        
        if debug: print(Color((r, g, b)))
        
        return Color((r, g, b))
    