from interface import InterfaceController

class StateController:

    # Variables
    def __init__(self):
        self.state = "Transfer"

    pass

    # Static instance

    instance = None

    # Class Methods

    def change_state_text(self):
        print("clicked Change State!")
        if self.state == "Transfer":
            self.state = "Receive"
        else:
            self.state = "Transfer"

        InterfaceController.get_instance().SetStateLabelText(self.state)

    pass

    def transfer_function(self):
        print("clicked Transfer File")
        input_text = InterfaceController.get_instance().text_box.get()
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
