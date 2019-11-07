"""
    INTERACTIVE SCRIPTING HELPER
    Avoid using this for any script, least it breaks after a change.
    
    Import syntax from interactive interpreter:
        from i import *
    Or run as:
        python -i i.py
"""

import time
import os
import sys
import inspect

from classes.features   import *
from classes.helper     import Helper
from classes.inputs     import Inputs
from classes.navigation import Navigation

import coordinates  as coords
import constants    as consts
import usersettings as uset

# Clear screen Windows
def   cls(): os.system("cls")
# Clear screen Linux
def clear(): os.system("clear")

# Show classes
def showClasses():
    clss = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    print(*[x[0] for x in clss], sep="\n")

# Show non class-related functions with cls=None
# Show methods and functions in the class if cls is provided
def showFuncs(cls=None):
    if cls is None:
        fncs = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
        print(*[x[0] for x in fncs], sep="\n")
    else:
        funcs = inspect.getmembers(cls, inspect.ismethod)
        if funcs != []:
            print("Methods:")
            for func in funcs: print(f"\t{func[0]}")
        funcs = inspect.getmembers(cls, inspect.isfunction)
        if funcs != []:
            print("Functions:")
            for func in funcs: print(f"\t{func[0]}")
  
# Show arguments of a function or method  
def showFunc(func):
    print(f"From module {inspect.getmodule(func).__name__}")
    print(f"\t{func.__qualname__} {inspect.signature(func)}")
    for line in inspect.getdoc(func).splitlines():
        print(f"\t{line}")

def i_help():
    print("* Use i_help() to print this message().")
    print("* You have cls() - Windows and clear() - Linux to clear the console.")
    print("*")
    print("* You can use showClasses() to show currently available classes.")
    print("* You can use showFuncs() to show non class-related functions.")
    print("* You can use showFuncs(class) to show the functions within a class.")
    print("* You can use showFuncs(obj) to show bound methods of a class instance.")
    print("* You can use showFunc(func) to show a function signature and documentation.")
    
print("Imported the Interactive Scripting Helper.")
print("This is meant to be used ONLY on an interactive Python session.")
print("This should be imported as:")
print("\tfrom i import *")
print("Or run as:")
print("\tpython -i i.py")
print()
i_help()
print()
print("Getting game window and initializing.")
try:
    Helper.init(True)
    print("Successfully initialized")
except Exception as e:
    print(str(e))
    print("Run Helper.init() manually")
print()
