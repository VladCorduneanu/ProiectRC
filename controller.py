from interface import InterfaceController
import logger
import enum
import socket
import queue
import threading
import frame


def data_write(data):
    sir_nou = ""
    for it in data:
        if it == '+' or it == '>' or it == '<' or it == '/' or it == '~':
            sir_nou = sir_nou + '/'
        sir_nou = sir_nou + it
    return sir_nou


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

        # citire fisier
        input_text = InterfaceController.get_instance().text_box.get()
        logger.Logger.write("Starting transfer of file: " + input_text)
        current_data=""
        try:
            file = open(input_text, "r")
            current_data = file.read()
            current_data = data_write(current_data)
            print("Read File succesfuly")
        except IOError:
            logger.Logger.write("Error: File does not appear to exist.")
            return

        packList = []

        rest = len(current_data) % 64
        intreg = len(current_data) - rest

        for i in range(0, intreg - 1, 64):
            packList.append(current_data[i:i + 63])

        if rest > 0:
            packList.append(current_data[intreg-1:])

        connpack = frame.Frame()
        connpack.type = 1
        connpack.total_number = len(packList)
        logger.Logger.write("Sending connection package")
        self.transmit_buffer.put(connpack.encode_message())

        isConnecting = 1
        isTransfering = 0
        isFinished = 0

        isWaiting = 0
        isSending = 0

        currentPackNumber = 0

        windowDim = 1

        while isConnecting == 1:
            if not self.receive_buffer.empty():

                data = self.receive_buffer.get()
                pachet = frame.Frame()
                pachet.decode_message(data)

                if pachet.type == 2:
                    windowDim = 1  # TODO
                    isConnecting = 0
                    isTransfering = 1
                    isSending = 1
                    isWaiting = 0

        while isTransfering == 1:
            if isSending == 1:
                packToSend = frame.Frame()
                packToSend.type = 3
                packToSend.frame_number = currentPackNumber
                packToSend.data = packList[currentPackNumber]
                packToSend.length = len(packToSend.data)

                logger.Logger.write("Sending data package: " + currentPackNumber.__str__())
                self.transmit_buffer.put(packToSend.encode_message())

                isSending = 0
                isWaiting = 1

            if isWaiting == 1:
                if not self.receive_buffer.empty():

                    data = self.receive_buffer.get()
                    ackPack = frame.Frame()
                    ackPack.decode_message(data)

                    if ackPack.type == 5:
                        currentPackNumber = ackPack.frame_number + 1

                        isSending = 1
                        isWaiting = 0
            if currentPackNumber == len(packList):
                isTransfering = 0
                isFinished = 1

        while isFinished == 1:
            endPack = frame.Frame()
            endPack.type = 4
            logger.Logger.write("Sending end package: ")
            self.transmit_buffer.put(endPack.encode_message())
            isFinished=0

    pass

    def receive_function(self):
        logger.Logger.write("Receive function triggered")
        receivedPackList = []

        isListening = 1
        isReceving = 0
        isFinished = 0

        isWaiting = 0
        isSendingAck = 0

        currentPack = 0;

        while isListening == 1:
            if not self.receive_buffer.empty():
                data = self.receive_buffer.get()
                connPack = frame.Frame()
                connPack.decode_message(data)
                if connPack.type == 1:
                    accConnPack = frame.Frame()
                    accConnPack.type = 2
                    accConnPack.window_size = 1  # TODO hardcoding
                    self.transmit_buffer.put(accConnPack.encode_message())
                    isListening = 0
                    isReceving = 1
                    isWaiting = 1
                    isSendingAck = 0
        while isReceving == 1:
            if isWaiting == 1:
                if not self.receive_buffer.empty():
                    data = self.receive_buffer.get()
                    receivedPack = frame.Frame()
                    receivedPack.decode_message(data)
                    if receivedPack.type == 3 and currentPack == receivedPack.frame_number:
                        receivedPackList.append(receivedPack.data)
                        currentPack = currentPack + 1
                        isWaiting = 0
                        isSendingAck = 1
                    elif receivedPack.type == 4:
                        isReceving = 0
                        isFinished = 1
                    else:
                        isSendingAck
            if isSendingAck == 1:
                ackPack = frame.Frame()
                ackPack.type = 5
                ackPack.frame_number = currentPack - 1
                ackPack.remaining_space = 1 #TODO hardcoding
                self.transmit_buffer.put(ackPack.encode_message())
                isSendingAck=0
                isWaiting=1
        while isFinished == 1:
            print("\n\n\n")

            for it in receivedPackList:
                print(it, end="")
            print("")
            isFinished = 0

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
                MESSAGE: str = self.transmit_buffer.get()
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
