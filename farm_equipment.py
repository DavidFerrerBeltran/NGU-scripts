"""Farming Script"""

import argparse
import colorama

from multiprocessing            import Process, Pipe, freeze_support
from multiprocessing.connection import Connection

from classes.helper     import Helper
from classes.features   import Adventure, Inventory
from classes.processing import Processing
from classes.inputs     import Inputs
from classes.window     import Window

import coordinates as coords

Helper.init()

def drop_printer(c :Connection, pend :int, looty :int) -> None:
    try:
        colorama.init()

        gold = 0
        maxgold = 0
        exp = 0
        AP = 0
        droplist = {}
        lines = 0

        while True:
            c.recv()
            bmp = Inputs.get_cropped_bitmap(*Window.gameCoords(*coords.OCR_ADV_LOG))
            c.send(True)

            logs = Processing.ocr(0,0,0,0, bmp=bmp).splitlines()
            found_last = False
            drops = []

            for x in reversed(logs):
                if not found_last and "dropped" in x: found_last = True
                if found_last:
                    if not "dropped" in x: break
                    elif "gold!" in x:
                        spl = x.split("dropped ")[1].split("gold!")
                        if len(spl) > 1: s = spl[0]
                        else: s = spl[0]

                        g = int(float(s.strip().lower()))
                        gold += g
                        maxgold = max(maxgold, g)

                    elif "EXP" in x : pass
                    elif "AP" in x: pass
                    else:
                        spl = x.split("dropped ")[1].split("!")
                        if len(spl) > 1: s = spl[0]
                        else: s = spl[0]
                        
                        if "Pendant" in s:
                            tier = s.count("Ascended")
                            s = f"{tier}x Ascended Pendant"
                            if tier >= pend: drops.append(s)
                        elif "looty" in s.lower():
                            looties = enumerate(["Looty McLootFace", "Sir Looty" , "King Looty", "Emperor Looty", "GALACTIC HERALD LOOTY", "SUPREME INTELLIGENCE LOOTY"], 1)
                            tier = 0
                            for tval, tname in looties: 
                                if tname in s: tier = tval
                            if tier >= looty: drops.append(s)

                        else: 
                            drops.append(s)
            
            drops.reverse()

            for drop in drops:
                if drop in droplist: droplist[drop] += 1
                else: droplist[drop] = 1

            print(f"\033[{lines+4}A", end="", flush=True)
            print(f"Gold:     {gold:.2e}", 40*" ")
            print(f"Max Gold: {maxgold:.2e}", 40*" ")
            print(f"EXP:      {exp}", 40*" ")
            print(f"AP:       {AP}", 40*" ")
            for drop in sorted(droplist): print(drop + ":", droplist[drop], 40*" ")
            lines = len(droplist)
    
    except KeyboardInterrupt: return

if __name__ == '__main__':
    freeze_support()

    try:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-z", "--zone", default=0, type=int,
            help="select which zone you wish to snipe")
        parser.add_argument(
            "-m", "--merge", default=0, type=int,
            help="set how many inventory slots to use for merging")
        parser.add_argument(
            "-b", "--boost", default=0, type=int,
            help="set how many inventory slots to use for boosting")
        parser.add_argument(
            "-n", "--number", default=20, type=int,
            help="set how many mobs to kill per cycle, before proceeding to do non-adventure things")
        parser.add_argument(
            "--all-mobs", action='store_true',
            help="set this flag to kill all mobs instead of bosses only")
        parser.add_argument(
            "--regular-only", action='store_true',
            help="set this flag to use regular attack only")
        parser.add_argument(
            "-p", "--pendant-tier", default=0, type=int,
            help="set the minimum tier of FP to be displayed on the loot list (FP is tier 0)")
        parser.add_argument(
            "-l", "--looty-tier", default=0, type=int,
            help="set the minimum tier of looty to be displayed on the loot list (McLootface is tier 1)")

        args = parser.parse_args()

        cparent, cchild = Pipe()
        dprinter = Process(target=drop_printer, args=(cchild, args.pendant_tier, ))
        dprinter.start()

        while True:
            Adventure.set_zone(args.zone)
            Adventure.set_idle(False)

            for _ in range(args.number):
                Adventure.snipe(bosses=not args.all_mobs, regular=args.regular_only)
                cparent.send(True)
                cparent.recv()
            Adventure.set_zone(1)

            Inventory.merge_inventory(args.merge)
            Inventory.boost_inventory(args.boost)
    
    except KeyboardInterrupt:
        print("Received a Keyboard Interruption, exiting...")
        Adventure.set_idle(True)
        exit()
