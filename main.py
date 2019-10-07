from tkinter import *


def main():
    # Interface Controller
    interface_controller = InterfaceController.get_instance()

    # Master
    interface_controller.master = Tk()
    interface_controller.master.geometry("600x600")

    # Frame
    interface_controller.frame = Frame(interface_controller.master, background="lightblue")
    interface_controller.frame.pack(fill="both", expand=True)

    # Change State Button
    interface_controller.change_state_button = Button(interface_controller.frame, text="Change State",
                                                      command=interface_controller.change_state)
    interface_controller.change_state_button.pack(side=BOTTOM, padx=5, pady=5)

    # State Label Text
    interface_controller.state_label_text = StringVar(interface_controller.master)
    interface_controller.state_label_text.set("State: Transfer")

    # State Label
    interface_controller.state_label = Label(interface_controller.frame,
                                             textvariable=interface_controller.state_label_text, font=20)
    interface_controller.state_label.pack(side=BOTTOM)

    # Transfer Button
    interface_controller.transfer_button = Button(interface_controller.frame, text="Transfer File",
                                                  command=interface_controller.transfer_file)
    interface_controller.transfer_button.pack(padx=5, pady=5)

    # Text Box for file path
    interface_controller.text_box = Entry(interface_controller.frame, width=200)
    interface_controller.text_box.pack(padx=5, pady=5)

    # MainLoop
    interface_controller.master.mainloop()


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
        print("clicked Transfer File")
        input_text = InterfaceController.get_instance().text_box.get()
        open(input_text, "+w")
    pass

    # TODO call State Controller to change the state and give the label what to write
    @staticmethod
    def change_state():
        print("clicked Change State!")
        InterfaceController.get_instance().change_state_text()
    pass

    # Class Methods

    def change_state_text(self):
        if self.state == "Transfer":
            self.state = "Receive"
        else:
            self.state = "Transfer"

        self.state_label_text.set("State: " + self.state)


if __name__ == "__main__":
    main()
