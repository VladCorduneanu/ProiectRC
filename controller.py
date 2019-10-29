from interface import InterfaceController
import logger


class StateController:

    # Variables
    def __init__(self):
        self.state = "Transfer"

    pass

    # Static instance

    instance = None

    # Class Methods


    def transfer_function(self):
        print("clicked Transfer File")
        input_text = InterfaceController.get_instance().text_box.get()
        logger.Logger.write("Transfer Function Has Been Triggered:" + input_text)
        try:
            open(input_text, "+w")
        except IOError:
            print("Error: File does not appear to exist.")

    pass

    @staticmethod
    def get_instance():
        if StateController.instance is None:
            StateController.instance = StateController()
        return StateController.instance

    pass
