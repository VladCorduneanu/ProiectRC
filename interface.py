from tkinter import *
import controller
from tkinter import filedialog
import logger
import threading


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
        self.S = None
        self.T = None
        self.timeoutScale = None
        self.windowSizeScale = None
        self.lostPercentScale = None
        # Variables
        self.state_label_text = None
        self.state = ""
        self.working_thread = None

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

        if self.state == "sender":
            # Text Box for file path
            self.text_box = Entry(self.frame, width=90)
            self.text_box.place(x=0, y=40)

            # Browse Button
            self.browse_button = Button(self.frame, text="Browse",
                                        command=self.file_dialog)
            self.browse_button.place(x=548, y=36)

            # scale for timeout
            self.timeoutScale = Scale(self.frame,from_=0, to=5, resolution=1, orient=HORIZONTAL, label="timeout")
            self.timeoutScale.place(x=230, y=70)
        else:
            self.windowSizeScale = Scale(self.frame, from_=1, to=5, resolution=1, orient=HORIZONTAL, label="window size")
            self.windowSizeScale.place(x=150, y=70)

            self.lostPercentScale = Scale(self.frame, from_=0, to=100, resolution=1, orient=HORIZONTAL, label="lost percent")
            self.lostPercentScale.place(x=360, y=70)
        # text label
        self.T = Text(self.frame,height=25, width=70)
        self.T.place(x=18, y=130)
        # exit call
        self.master.protocol("WM_DELETE_WINDOW", self.close_me)

    pass

    # Static instance
    instance = None

    # Static Methods

    # singleton method for interface
    @staticmethod
    def get_instance():
        if InterfaceController.instance is None:
            InterfaceController.instance = InterfaceController()
        return InterfaceController.instance

    # the method that trigger the transfer button -> transfer button callback
    @staticmethod
    def transfer_file():
        InterfaceController.get_instance().working_thread = threading.\
            Thread(target=InterfaceController.get_instance().transfer_file_thread)
        InterfaceController.get_instance().working_thread.start()
    pass

    @staticmethod
    def transfer_file_thread():
        if logger.state == "sender":
            controller.StateController.get_instance().transfer_function()
        elif logger.state == "receiver":
            controller.StateController.get_instance().receive_function()
        else:
            print("The state doesn't exist")
            return

    pass

    # setter for state
    def set_state(self, state):
        self.state = state
        controller.StateController.get_instance().set_state(state)

    # brows file method -> browse button callback
    def file_dialog(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                              filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        self.text_box.insert(0, filename)

    pass

    # method that close the app from interface -> quit callback
    def close_me(self):
        self.working_thread.join()
        controller.StateController.get_instance().close_app()
        self.master.destroy()

    pass

    def get_timeout(self):
        return self.timeoutScale.get()

    def get_window(self):
        return self.windowSizeScale.get()

    def get_percent(self):
        return self.lostPercentScale.get()