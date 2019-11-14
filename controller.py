from interface import InterfaceController
import logger
import enum
import socket
import queue
import threading


class States(enum.Enum):
    SENDER = "sender"
    RECEIVER = "receiver"


class StateController:

    # Variables
    def __init__(self):
        self.state = States.RECEIVER
        self.receive_buffer = queue.Queue()
        self.transmit_buffer = queue.Queue()
        self.receive_thread: threading.Thread = threading.Thread()
        self.transmit_thread: threading.Thread = threading.Thread()

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
            self.transmit_buffer.put("inceput")
            for it in file_text:
                self.transmit_buffer.put(it)
            self.transmit_buffer.put("final")
        except IOError:
            print("Error: File does not appear to exist.")

    pass

    def set_state(self, state):
        if state == "sender":
            self.state = States.SENDER
        else:
            self.state = States.RECEIVER

        argument = "receive"
        self.receive_thread = threading.Thread(target=self.thread_starter, kwargs=dict(mode=argument))
        self.receive_thread.start()

        argument = "transmit"
        self.receive_thread = threading.Thread(target=self.thread_starter, kwargs=dict(mode=argument))
        self.receive_thread.start()

    pass

    def sender(self):
        UDP_IP = "127.0.0.1"
        if self.state == States.RECEIVER:
            UDP_PORT = 5005
        else:
            UDP_PORT = 5006

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        while not self.kill_thread:
            if not self.transmit_buffer.empty():
                MESSAGE = self.transmit_buffer.get()
                sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
                #print("sent message", MESSAGE, "\n")

        sock.close()
        pass

    def receiver(self):
        if self.state == States.RECEIVER:
            UDP_PORT = 5006
        else:
            UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind(('', UDP_PORT))
        while not self.kill_thread:
            data = sock.recv(100)
            self.receive_buffer.put(data.decode())
            if data.decode() == "final":
                finish = False
                fisier = ""
                while not finish:
                    if self.receive_buffer.get() == "inceput":
                        pack = self.receive_buffer.get()
                        while pack != "final":
                            fisier = fisier + pack + "\n"
                            pack = self.receive_buffer.get()
                        print(fisier)
                        finish = True
            print("received message", data, "\n")

        sock.close()
        pass

    @staticmethod
    def thread_starter(mode: str):
        if mode == "receive":
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
