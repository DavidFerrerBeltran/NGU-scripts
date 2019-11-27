"""AP farming script."""

# Helper classes
from classes.helper   import Helper
from classes.features import Adventure, MoneyPit

Helper.init(True)
Helper.requirements()

while True:  # main loop
    Adventure.old_itopod_ap(600)
    MoneyPit.pit()
