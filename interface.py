from tkinter import *
import controller
from tkinter import filedialog


class InterfaceController:
    # Members
    def __init__(self):
        # Buttons and Tkinter components
        self.transfer_button = None
        self.browse_button = None
        self.state_label = None
        self.text_box = None
        self.master = None
        self.frame = None

        # Variables
        self.state_label_text = None
        self.state = ""

        pass

    # Init function

    def init_interface_controller(self):
        # Master
        self.master = Tk()
        self.master.geometry("600x600")
        self.master.title("The " + self.state)

        # Frame
        self.frame = Frame(self.master, background="lightblue")
        self.frame.pack(fill="both", expand=True)
        self.master.resizable(False, False)

        # State Label Text
        self.state_label_text = StringVar(self.master)
        self.state_label_text.set("State: " + self.state)

        # State Label
        self.state_label = Label(self.frame,
                                 textvariable=self.state_label_text, font=20)
        self.state_label.pack(side=BOTTOM)

        # Transfer Button
        self.transfer_button = Button(self.frame, text="Transfer File",
                                      command=self.transfer_file)
        self.transfer_button.place(x=270, y=5)

        # Text Box for file path
        self.text_box = Entry(self.frame, width=90)
        self.text_box.place(x=0, y=40)

        # Browse Button
        self.browse_button = Button(self.frame, text="Browse",
                                    command=self.file_dialog)
        self.browse_button.place(x=548, y=36)

        self.master.protocol("WM_DELETE_WINDOW", self.close_me)

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
        controller.StateController.get_instance().transfer_function()

    pass

    # TODO call State Controller to change the state and give the label what to write

    def set_state(self, state):
        self.state = state
        controller.StateController.get_instance().set_state(state)

    def file_dialog(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                              filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        self.text_box.insert(0, filename)

    pass

    def close_me(self):
        controller.StateController.get_instance().close_app()
        self.master.destroy()
    pass
