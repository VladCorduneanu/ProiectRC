import logger
import enum
import socket
import queue
import threading
import frame
import time
import datetime
import functions
import PackageFactory


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
        self.frameFactory = PackageFactory.PackageFacatory()

    pass

    # Static instance

    instance = None

    # Class Methods

    def transfer_function(self):
        logger.Logger.write("Transfer function triggered")

        #   text to transfer
        packList:  [] = functions.getPackagesToSend()

        if packList == None:
            return

        # trimitere pachet de conectare care contine numarul de pachete al fisierului ce va fi trimis
        totalPacks = len(packList)
        connpack = self.frameFactory.getPackage("connect", totalPacks, None, None, None)

        logger.Logger.write("Sending connection package")
        print("Sending conn pack")
        self.transmit_buffer.put(connpack.encode_message())

        # starile pentru transmiterea fisierului
        isConnecting = 1
        isTransfering = 0
        isFinished = 0
        isWaiting = 0
        isSending = 0

        # timer timeout
        lastResponse = datetime.datetime.now()

        # initializare numar pachet trimis
        currentPackNumber = 1

        # initializare numar pachet primit

        currentReceivedPack = 0

        # inceperea conectarii intre sender si receiver
        while isConnecting == 1:
            if (datetime.datetime.now() - lastResponse).total_seconds() > 5:
                self.transmit_buffer.put(connpack.encode_message())
                print("Sending conn pack")
                lastResponse = datetime.datetime.now()
            # asteptare raspuns pentru pachet de conectare
            if not self.receive_buffer.empty():

                data = self.receive_buffer.get()
                pachet = frame.Frame()
                pachet.decode_message(data)

                # verificare pachet de conectare reusita si primire dimensiune fereastra
                if pachet.type == 5:
                    lastResponse = datetime.datetime.now()
                    windowDim = pachet.window_size
                    isConnecting = 0
                    isTransfering = 1
                    isSending = 1
                    isWaiting = 0

        # inceperea transferului de pachete ce contin datele fisierului
        while isTransfering == 1:
            # schimbare stare
            buffer_size = currentPackNumber - currentReceivedPack
            if buffer_size - 1 >= windowDim or currentPackNumber > len(packList):
                isSending = 0
                isWaiting = 1

            # trimitire pachete
            if isSending == 1:
                # creare pachet
                packToSend = self.frameFactory.getPackage("data", None, None, currentPackNumber,
                                                     packList[currentPackNumber - 1])

                # transmitere
                logger.Logger.write("Sending data package: " + currentPackNumber.__str__())
                self.transmit_buffer.put(packToSend.encode_message())

                print("Sender: Am transmis pachetul numarul: " + currentPackNumber.__str__())
                currentPackNumber = currentPackNumber + 1

                # verificare sosire pachet
                if not self.receive_buffer.empty():

                    lastResponse = datetime.datetime.now()
                    # decodare mesaj primit
                    data = self.receive_buffer.get()
                    ackPack = frame.Frame()
                    ackPack.decode_message(data)

                    # verificare confirmare
                    if ackPack.type == 5:
                        currentReceivedPack = ackPack.frame_number
                        print("Sender: Am primit pachetul numarul: " + str(currentReceivedPack))
                        windowDim = ackPack.window_size

            # verificare finalizare transfer
            if currentReceivedPack == len(packList):
                isTransfering = 0
                isFinished = 1

            # asteptare confirmare pachet
            if isWaiting == 1:
                # verificare sosire pachet
                if not self.receive_buffer.empty():
                    lastResponse = datetime.datetime.now()
                    # decodare mesaj primit
                    data = self.receive_buffer.get()
                    ackPack = frame.Frame()
                    ackPack.decode_message(data)

                    # verificare confirmare
                    if ackPack.type == 5:
                        currentReceivedPack = ackPack.frame_number
                        windowDim = ackPack.window_size
                        isSending = 1
                        isWaiting = 0
                        print(
                            "Sender: Am primit un ack, pot transmite iar, pachet primit: " + ackPack.frame_number.__str__() + "windowSize " + windowDim.__str__())
                else:
                    if (datetime.datetime.now() - lastResponse).total_seconds() > 15:
                        lastResponse = datetime.datetime.now()
                        print("TIMEOUT!!!")
                        isWaiting = 0
                        isSending = 1
                        currentPackNumber = currentReceivedPack + 1

        # transmitere pachet de end in caz de terminare transfer
        while isFinished == 1:
            print("Sender: Transmit pachetul de finish ")
            endPack = self.frameFactory.getPackage("final",None,None,None,None)
            logger.Logger.write("Sending end package: ")
            self.transmit_buffer.put(endPack.encode_message())
            isFinished = 0

    pass

    def receive_function(self):
        logger.Logger.write("Receive function triggered")
        receivedPackList = []

        # starile pentru receptionarea fisierului
        isListening = 1
        isReceving = 0
        isFinished = 0
        isWaiting = 0
        isSendingAck = 0
        length = 0

        # initializare numar pachet primit
        currentPack = 1

        windowDim = 5

        # asteptare pachet de conectare
        while isListening == 1:
            if not self.receive_buffer.empty():
                data = self.receive_buffer.get()
                connPack = frame.Frame()
                connPack.decode_message(data)
                length = connPack.total_number

                # verificare pachet primit
                if connPack.type == 1:
                    # transmitere pachet conectare reusita si dimnesiunea ferestrei

                    accConnPack = self.frameFactory.getPackage("ack",None,windowDim,0,None)

                    self.transmit_buffer.put(accConnPack.encode_message())
                    print("Receiver: Sending conn pack")
                    # schimbare stare
                    isListening = 0
                    isReceving = 1
                    isWaiting = 1
                    isSendingAck = 0

        # primire pachete care contin datele fisierului
        while isReceving == 1:
            # asteptare pachet de date
            if isWaiting == 1:
                if not self.receive_buffer.empty():
                    data = self.receive_buffer.get()
                    receivedPack = frame.Frame()
                    receivedPack.decode_message(data)
                    print(length)
                    # verificare tip pachet si numar pachet trimis
                    if receivedPack.type == 3 and currentPack == receivedPack.frame_number:
                        receivedPackList.append(receivedPack.data)
                        print(
                            "Receiver am primit un pachet corect si ii generez timp de prelucrare, pachetu: " + currentPack.__str__())
                        print("Receiver Prelucrez...")
                        currentPack = currentPack + 1

                        currentTime = datetime.datetime.now()

                        # generare timp de prelucrare
                        time.sleep(functions.genTp())

                        elapsedTime = (datetime.datetime.now() - currentTime).total_seconds()

                        # calculare dimensiune fereastra
                        windowDim = functions.genWindow(elapsedTime)

                        # pachet trimis corect, trimitere ack
                        print("Receiver Am terminar prelucrarea si vreau sa trimit ack")
                        isWaiting = 0
                        isSendingAck = 1
                    elif receivedPack.type == 4 or length == currentPack - 1:
                        print("Receiver: Am receptionat pachetul final")
                        # schimbare stare: pachet final receptionat
                        isReceving = 0
                        isFinished = 1
                        isSendingAck = 1
                    else:
                        isWaiting = 0
                        isSendingAck = 1

            # trimitrea ack pentru pachet receptionat
            if isSendingAck == 1:
                # creare pachet
                ackPack = self.frameFactory.getPackage("ack",None,windowDim,currentPack -1,None)
                print("Receiver: trimtit ack pentru pachetul: " + (currentPack - 1).__str__())
                self.transmit_buffer.put(ackPack.encode_message())
                # schimbare stare
                isSendingAck = 0
                isWaiting = 1

        # stare terminare transfer
        while isFinished == 1:
            if length == currentPack - 1:
                print('Transfer reusit!!!')
            else:
                print("Receiver: am primti pachetul de final -NEREUSIT")
            # afisare pachete transmise

            print("\n\n\n\t\t\t\t\tMESAJE DECODATE")
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

                lost = functions.getLost(0)

                if not lost:
                    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
                else:
                    ackPack = frame.Frame()
                    ackPack.decode_message(MESSAGE)

                    print(
                        'S-a pierdut la transmisie pachetul cu tipul:' + ackPack.type.__str__() +
                        'si numarul: ' + ackPack.frame_number.__str__())

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
