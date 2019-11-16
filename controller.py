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
        logger.Logger.write("Transfer function triggered")

        tip = "1"
        conn_pack = tip
        logger.Logger.write("Sending connection package")
        self.transmit_buffer.put(conn_pack)
        isTransfering = 1

        while isTransfering == 1:
            if not self.receive_buffer.empty():
                pack = self.receive_buffer.get()
                if pack[0] == "2":

                    dim = int(pack[1:])

                    input_text = InterfaceController.get_instance().text_box.get()
                    logger.Logger.write("Starting transfer of file: " + input_text)

                    file_data = []
                    packages = []
                    try:
                        file = open(input_text, "r")

                        while True:
                            current_data = file.read(dim)
                            if current_data == '':
                                break
                            file_data.append(current_data)
                    except IOError:
                        logger.Logger.write("Error: File does not appear to exist.")

                    tip = "3"
                    nr_pachet = 0
                    for it in file_data:
                        nr_pachet = nr_pachet + 1
                        current_package = tip + " " + str(nr_pachet) + " " + str(len(it)) + " " + it
                        packages.append(current_package)
                    print("da")

    pass

    def receive_function(self):
        logger.Logger.write("Receive function triggered")
        isReceving = 1
        isConnected = 0
        dim = 64
        while isReceving == 1:
            if not self.receive_buffer.empty():
                pack = self.receive_buffer.get()
                if pack[0] == "1":
                    connected_pack = "2" + str(dim)
                    self.transmit_buffer.put(connected_pack)
                    isConnected = 1
                #if isConnected:



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
        self.transmit_thread = threading.Thread(target=self.thread_starter, kwargs=dict(mode=argument))
        self.transmit_thread.start()

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
            # print(self.kill_thread)
            if not self.transmit_buffer.empty():
                MESSAGE : str = self.transmit_buffer.get()
                sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
                # print("sent message", MESSAGE, "\n")

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
            # if data.decode() == "final":
            #     finish = False
            #     fisier = ""
            #     while not finish:
            #         if self.receive_buffer.get() == "inceput":
            #             pack = self.receive_buffer.get()
            #             while pack != "final":
            #                 fisier = fisier + pack + "\n"
            #                 pack = self.receive_buffer.get()
            #             print(fisier)
            #             finish = True
            print("received message", data, "\n")

        sock.close()

    pass

    def close_app(self):
        if StateController.get_instance().receive_thread:
            StateController.get_instance().kill_thread = True
            if self.state == States.RECEIVER:
                UDP_PORT = 5006
            else:
                UDP_PORT = 5005

            sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
            sock.bind(('', 5007))
            string = "closing"
            UDP_IP = "127.0.0.1"
            sock.sendto(string.encode(), (UDP_IP, UDP_PORT))

        if StateController.get_instance().transmit_thread:
            StateController.get_instance().kill_thread = True

        print(StateController.get_instance().transmit_thread.is_alive())

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
