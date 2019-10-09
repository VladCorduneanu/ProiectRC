from tkinter import *


def main():
    # Interface Controller
    interface_controller = InterfaceController.get_instance()

    # State Controller
    state_controller = StateController.get_instance()

    # Master Loop
    interface_controller.get_instance().master.mainloop()



class InterfaceController:
    # Members
    def __init__(self):
        # Buttons and Tkinter components
        self.transfer_button = None
        self.change_state_button = None
        self.state_label = None
        self.text_box = None
        self.master = None
        self.frame = None

        # Variables
        self.state_label_text = None
        self.state = "Transfer"

        # Init Variables
        self.InitInterfaceController()
        # TODO INIT
        pass

    # Init function

    def InitInterfaceController(self):
        # Master
        self.master = Tk()
        self.master.geometry("600x600")

        # Frame
        self.frame = Frame(self.master, background="lightblue")
        self.frame.pack(fill="both", expand=True)

        # Change State Button
        self.change_state_button = Button(self.frame, text="Change State",
                                          command=self.change_state)
        self.change_state_button.pack(side=BOTTOM, padx=5, pady=5)

        # State Label Text
        self.state_label_text = StringVar(self.master)
        self.state_label_text.set("State: Transfer")

        # State Label
        self.state_label = Label(self.frame,
                                 textvariable=self.state_label_text, font=20)
        self.state_label.pack(side=BOTTOM)

        # Transfer Button
        self.transfer_button = Button(self.frame, text="Transfer File",
                                      command=self.transfer_file)
        self.transfer_button.pack(padx=5, pady=5)

        # Text Box for file path
        self.text_box = Entry(self.frame, width=200)
        self.text_box.pack(padx=5, pady=5)

    pass

    # Static instance
    instance = None

    # Static Methods
    @staticmethod
    def get_instance():
        if InterfaceController.instance is None:
            InterfaceController.instance = InterfaceController()
        return InterfaceController.instance

    @staticmethod
    def transfer_file():
        StateController.get_instance().transfer_function()

    pass

    # TODO call State Controller to change the state and give the label what to write
    @staticmethod
    def change_state():
        StateController.get_instance().change_state_text()

    pass

    def SetStateLabelText(self, new_text):
        self.state_label_text.set("State: " + new_text)

    pass


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

if __name__ == "__main__":
    main()

