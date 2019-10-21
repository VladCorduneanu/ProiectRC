from controller import StateController
from interface import InterfaceController
import logger


def main():
    # Start of program
    logger.Logger.write("Program Has Started")
    logger.Logger.flush()

    # Interface Controller
    interface_controller = InterfaceController.get_instance()
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

    logger.Logger.on_exit()


if __name__ == "__main__":
    main()
