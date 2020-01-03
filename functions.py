import random


def genTp():
    return random.random() * 6


def genWindow(elapsed_time):
    if elapsed_time < 1.5:
        return 5
    elif elapsed_time < 3:
        return 4
    elif elapsed_time < 5:
        return 3
    elif elapsed_time < 5.5:
        return 2
    else:
        return 1


def getLost(percent):
    var = 100 * random.random()
    if var <= percent:
        return True
    else:
        return False
