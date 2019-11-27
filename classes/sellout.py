"""Handles the Sellout Shop."""

import datetime

import coordinates as coords

from classes.navigation import Navigation
from classes.processing import Processing
from classes.inputs     import Inputs

class _SelloutShop:
    @staticmethod
    def eat_muffin(buy :bool =False) -> None:
        """Eat a MacGuffin Muffin if it's not active.
        
        Keyword arguments:
        buy -- set to True if you wish to buy a muffin if you have enough
        AP and you currently have 0 muffins.
        """
        Navigation.sellout_boost_2()
        muffin_status = Processing.ocr(*coords.OCR_MUFFIN).lower()
        if "have: 0" in muffin_status and "inactive" in muffin_status:
            print(muffin_status)
            if buy:
                try:
                    ap = int(Processing.remove_letters(Processing.ocr(*coords.OCR_AP)))
                except ValueError:
                    print("Couldn't get current AP")
                if ap >= 50000:
                    print(f"Bought MacGuffin Muffin at: {datetime.datetime.now()}")
                    Inputs.click(*coords.SELLOUT_MUFFIN_BUY)
                    Navigation.confirm()
            else:
                return
        else:
            return
        Inputs.click(*coords.SELLOUT_MUFFIN_USE)
        print(f"Used MacGuffin Muffin at: {datetime.datetime.now()}")