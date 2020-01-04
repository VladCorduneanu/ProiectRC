import datetime
import random
import logger
from interface import InterfaceController


# encode function for data
def data_write(data):
    sir_nou = ""
    for it in data:
        if it == '+' or it == '>' or it == '<' or it == '/' or it == '~':
            sir_nou = sir_nou + '/'
        sir_nou = sir_nou + it
    return sir_nou


# generate processing time function
def genTp(scale):
    return random.random() * scale


# generating window size function
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


# generating time for lost package
def getLost(percent):
    var = 100 * random.random()
    if var <= percent:
        return True
    else:
        return False


def getPackagesToSend():
    logger.Logger.write("Writing file...")

    input_text = InterfaceController.get_instance().text_box.get()
    current_data = ""
    try:
        file = open(input_text, "r")
        current_data = file.read()
        current_data = data_write(current_data)
        logger.Logger.write("Read File successful")
    except IOError:
        logger.Logger.write("Error: File does not appear to exist.")
        return None

    packList = []

    # establish the number of packages
    rest = len(current_data) % 64
    intreg = len(current_data) - rest

    for i in range(0, intreg - 1, 64):
        packList.append(current_data[i:i + 63])

    if rest > 0:
        packList.append(current_data[intreg - 1:])

    # return packages
    return packList
