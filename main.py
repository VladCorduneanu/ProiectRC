from controller import StateController
from interface import InterfaceController


def main():
    # Interface Controller
    interface_controller = InterfaceController.get_instance()

    # State Controller
    state_controller = StateController.get_instance()

    # Master Loop
    interface_controller.get_instance().master.mainloop()


if __name__ == "__main__":
    main()
