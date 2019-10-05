from tkinter import *





def main():
    interface_controller = InterfaceController.get_instance()
    interface_controller.master = Tk()
    # interface_controller.back = Frame(master=interface_controller.master,
    #                                   width=500, height=500, bg='black')
    # interface_controller.back.pack()
    interface_controller.button = Button(interface_controller.master, text="Transfer File",
                                         command=interface_controller.transfer_file)
    interface_controller.button.pack()
    interface_controller.text_box = Entry(interface_controller.master)
    interface_controller.text_box.pack()

    mainloop()


class InterfaceController:
    def __init__(self):
        self.button = None
        self.text_box = None
        self.master = None
        # self.back = None
        pass

    instance = None

    @staticmethod
    def get_instance():
        if InterfaceController.instance is None:
            InterfaceController.instance = InterfaceController()
        return InterfaceController.instance

    @staticmethod
    def transfer_file():
        print("clicked OK!")
        input_text = InterfaceController.get_instance().text_box.get()
        open(input_text, "+w")
    pass


if __name__ == "__main__":
    main()
