"""Minimalist questing script"""

from classes.helper   import Helper
from classes.features import Questing

Helper.init(True)
while Questing.start_major(idle=False, butter=False):
    Questing.manual(30)
