from controller import StateController
from interface import InterfaceController
import logger
import sys
import threading


def main():
    # Set state of program
    if len(sys.argv) != 2:
        print("The application need exactly one argument: sender or receiver.")
        return
    if sys.argv[1] == "sender":
        print("The application started as sender.")
        state = "sender"
    elif sys.argv[1] == "receiver":
        state = "receiver"
        print("The application started as receiver.")
    else:
        print("The name of argument is incorrect. It must be: sender or receiver.")
        return

    # Start of program
    logger.Logger.write("Program Has Started")
    logger.Logger.flush()

    # Interface Controller
    interface_controller = InterfaceController.get_instance()
    interface_controller.set_state(state)
    interface_controller.init_interface_controller()
    logger.Logger.write("Init Interface Controller")
    logger.Logger.flush()

    # State Controller
    state_controller = StateController.get_instance()
    logger.Logger.write("Init State Controller")
    logger.Logger.flush()

    # Master Loop
    logger.Logger.write("Entering Main Loop")
    logger.Logger.flush()
    interface_controller.get_instance().master.mainloop()

    state_controller.get_instance().kill_thread = True

    logger.Logger.on_exit()


if __name__ == "__main__":
    main()
