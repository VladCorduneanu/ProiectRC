from interface import InterfaceController
import logger
import enum
import socket
import queue


class States(enum.Enum):
    SENDER = "sender"
    RECEIVER = "receiver"


class StateController:

    # Variables
    def __init__(self):
        self.state = States.RECEIVER
        self.buffer = queue.Queue()
        self.kill_thread = False

    pass

    # Static instance

    instance = None

    # Class Methods

    def transfer_function(self):
        print("clicked Transfer File")
        input_text = InterfaceController.get_instance().text_box.get()
        logger.Logger.write("Transfer Function Has Been Triggered:" + input_text)
        try:
            file = open(input_text, "r")
            file_text = file.readlines()
            for it in file_text:
                self.buffer.put(it)
        except IOError:
            print("Error: File does not appear to exist.")

    pass

    def set_state(self, state):
        if state == "sender":
            self.state = States.SENDER
        else:
            self.state = States.RECEIVER

    pass

    def sender(self):
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        while not self.kill_thread:
            if not self.buffer.empty():
                MESSAGE = self.buffer.get()
                sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
                print("sent message", MESSAGE, "\n")

        sock.close()
        pass

    def receiver(self):
        UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind(('', UDP_PORT))
        while not self.kill_thread:
            data = sock.recv(100)
            print("received message", data, "\n")

        sock.close()
        pass

    @staticmethod
    def thread_starter():
        if StateController.get_instance().state == States.RECEIVER:
            StateController.get_instance().receiver()
        else:
            StateController.get_instance().sender()

    pass

    @staticmethod
    def get_instance():
        if StateController.instance is None:
            StateController.instance = StateController()
        return StateController.instance

    pass
