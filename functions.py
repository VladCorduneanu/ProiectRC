import random
import logger
from interface import InterfaceController


def data_write(data):
    sir_nou = ""
    for it in data:
        if it == '+' or it == '>' or it == '<' or it == '/' or it == '~':
            sir_nou = sir_nou + '/'
        sir_nou = sir_nou + it
    return sir_nou


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


def getPackagesToSend():
    # citire fisier
    input_text = InterfaceController.get_instance().text_box.get()
    logger.Logger.write("Starting transfer of file: " + input_text)
    current_data = ""
    try:
        file = open(input_text, "r")
        current_data = file.read()
        current_data = data_write(current_data)
        print("Read File succesfuly")
    except IOError:
        logger.Logger.write("Error: File does not appear to exist.")
        return None

    packList = []

    # stablirie numar pachete
    rest = len(current_data) % 64
    intreg = len(current_data) - rest

    for i in range(0, intreg - 1, 64):
        packList.append(current_data[i:i + 63])

    if rest > 0:
        packList.append(current_data[intreg - 1:])
    # returnarea pachete
    return packList
