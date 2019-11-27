from classes.helper   import Helper
from classes.features import Adventure

Helper.init()
for x in range(1, 100):
    Adventure.set_zone(x)
    print(Adventure.get_zone(), Adventure.get_zonename())