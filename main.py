import argparse
import itertools
from math import ceil
from multiprocessing import Pool
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("length", help="the maximum length of an upgrade permutation to check", type=int)
parser.add_argument("turncount", help="the number of turns over which to check these permutations", type=int)
parser.add_argument("-v", "--verbose", help="never, NEVER use this", action="store_true")
parser.add_argument("-j", "--jobs", help="multithreading with N jobs", type=int, default = None)
priorityGroup = parser.add_mutually_exclusive_group(required=True)
priorityGroup.add_argument("-i", "--prioritize-income", help="the best upgrade permutation has the most income", action="store_true")
priorityGroup.add_argument("-m", "--prioritize-money", help="the best upgrade permutation has the most money", action="store_true")
parser.add_argument("-l", "--little-bit-verbose", help="please merge with -v or just delete -v", action="store_true")
args = parser.parse_args()
if __name__ == "__main__":
    if args.prioritize_income:
        print("Prioritizing permutations that end with the most income.")
    elif args.prioritize_money:
        print("Prioritizing permutations that end with the most money.")
    else:
        print("Error: unknown priority. This message should not appear.")

MONEY_PER = 0
STREAK_BONUS = 1
MULTIPLIER = 2
upgrades = [
[1, 5, 50, 100, 500, 2000, 5000, 10000, 250000, 1000000],
[2, 20, 100, 200, 1000, 4000, 10000, 50000, 1000000, 5000000],
[1, 1.5, 2, 3, 5, 8, 12, 18, 30, 100]
]
upgradeCosts = [
[0, 10, 100, 1000, 10000, 75000, 300000, 1000000, 10000000, 100000000],
[0, 15, 150, 1500, 15000, 115000, 450000, 1500000, 15000000, 200000000],
[0, 50, 300, 2000, 12000, 85000, 700000, 6500000, 65000000, 1000000000],
]

def moneyPerQuestion(indices):
    return ceil(upgrades[MULTIPLIER][indices[2]] * (upgrades[MONEY_PER][indices[0]] + upgrades[STREAK_BONUS][indices[1]]))

def nameUpgrade(upgrade):
    return ["Money Per Question", "Streak Bonus", "Multiplier"][upgrade]

def questionsToGet(permutation):
    money = 1 # If you get all questions right, we can just hardcode turn 1
    turns = 1 # so it's already been 1 turn
    indices = [0, 0, 0] # moneyPer, streakBonus, multiplier
    if args.verbose:
        print("Turn 1: Money is now 1")
    for upgrade in permutation:
        while money < upgradeCosts[upgrade][indices[upgrade] + 1]:
            turns += 1
            money += moneyPerQuestion(indices)
            if args.verbose:
                print(f"Turn {turns}: Money is now {money}")
        money -= upgradeCosts[upgrade][indices[upgrade] + 1]
        indices[upgrade] += 1
        if args.verbose:
            print(f"Purchased upgrade {nameUpgrade(upgrade)}. Money is now {money}")
    return turns, money

def evaluatePermOverTurns(permutation, totalTurns):
    money = 1 # If you get all questions right, we can just hardcode turn 1
    turns = 1 # so it's already been 1 turn
    indices = [0, 0, 0] # moneyPer, streakBonus, multiplier
    if args.verbose:
        print("Turn 1: Money is now 1")
    for upgrade in permutation:
        while money < upgradeCosts[upgrade][indices[upgrade] + 1]:
            turns += 1
            money += moneyPerQuestion(indices)
            if args.verbose:
                print(f"Turn {turns}: Money is now {money}")
            if turns >= totalTurns:
                return money, indices
        money -= upgradeCosts[upgrade][indices[upgrade] + 1]
        indices[upgrade] += 1
        if args.verbose:
            print(f"Purchased upgrade {nameUpgrade(upgrade)}. Money is now {money}")
    return money, indices
        
# This function doesn't work well. Not sure why.
#def brute_force_perm(perm_so_far, length):
#    if not length:
#        if args.verbose:
#            print(questionsToGet(perm_so_far))
#        return questionsToGet(perm_so_far)
#    for upgrade in range(3): # 3 because there are 3 upgrades: 0, 1, 2
#        a = brute_force_perm(perm_so_far + [upgrade], length - 1)
#        if a:
#            return a
#    return False

def moneyIncome(perm):
    money, indices = evaluatePermOverTurns(perm, args.turncount)
    income = moneyPerQuestion(indices)
    return money, income

def getBestPerm(perms):
    bestPerm = [[], 0, 0]
    for perm in perms:
        money, income = moneyIncome(perm)
        if args.verbose:
            print(f"{perm}: ${money}, income of ${income}")
        if args.prioritize_income:
            if income > bestPerm[2] or (income == bestPerm[2] and money > bestPerm[1]):
                bestPerm = [perm, money, income]
        else:
            if money > bestPerm[1] or (money == bestPerm[1] and income > bestPerm[2]):
                bestPerm = [perm, money, income]
    return bestPerm

def filterBadPerm(perm):
    return perm.count(0) < 10 and perm.count(1) < 10 and perm.count(2) < 10

def upgradesBought(perm):
    money = 1 # If you get all questions right, we can just hardcode turn 1
    turns = 1 # so it's already been 1 turn
    indices = [0, 0, 0] # moneyPer, streakBonus, multiplier
    for upgradeIndex in range(len(perm)):
        upgrade = perm[upgradeIndex]
        while money < upgradeCosts[upgrade][indices[upgrade] + 1]:
            turns += 1
            money += moneyPerQuestion(indices)
            if args.little_bit_verbose:
                print(f"Turn {turns}: Money is now {money}")
            if turns >= args.turncount:
                return sum(indices)
        money -= upgradeCosts[upgrade][indices[upgrade] + 1]
        if args.little_bit_verbose:
            print(f"Purchased upgrade {nameUpgrade(upgrade)} costing ${upgradeCosts[upgrade][indices[upgrade] + 1]}. Money is now ${money}.")
        indices[upgrade] += 1
    return sum(indices)

bestPerm = "This message should not appear :)"
if __name__ == '__main__':
    print("Timestamp:", datetime.now().time())
    permList = list(filter(filterBadPerm, itertools.product([0, 1, 2], repeat=args.length)))
    print(len(permList), "permutations to check.")
    if args.jobs:
        print(f"Initializing pool with {args.jobs} jobs") 
        chunks = [permList[i::args.jobs] for i in range(args.jobs)]
        pool = Pool(args.jobs)
        bestPerm = getBestPerm([i[0] for i in pool.map(getBestPerm, chunks, 1)])
    else:
        bestPerm = getBestPerm(permList)
    print(f"The best permutation was {bestPerm[0]}, which made ${bestPerm[1]} with an income of ${bestPerm[2]}.")
    print(f"Purchased {upgradesBought(bestPerm[0])}/{args.length} upgrades.")
