"""Challenge start script."""

import argparse

# Helper classes
from classes.challenge import Challenge
from classes.features import Adventure, GoldDiggers, MoneyPit
from classes.helper import Helper

parser = argparse.ArgumentParser(epilog='\n'.join(Challenge.list()), formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-c", "--challenge", required=True, type=int, help="select which challenge you wish to run (1-11)")
parser.add_argument("-t", "--times", default=1, type=int, help="number of times to run challenge")
parser.add_argument("-i", "--idle", action='store_true', help="run idle loop after finishing running")
parser.add_argument("-g", "--guffin", action='store_true', help="run rebirths equal or longer to 30' to get guff buffs.")
args = parser.parse_args()

Helper.init(True)
Helper.requirements()

print(f"Running challenge #{Challenge.list()[args.challenge-1]} {args.times} times")
for x in range(args.times):
    Challenge.start_challenge(args.challenge, guff=args.guffin)

print("Finished doing all challenges")
if args.idle:
    print("Engaging idling loop")
    while True:  # main loop
        Adventure.old_itopod_snipe(300)
        MoneyPit.pit()
        GoldDiggers.activate()
else: print("Exiting")
