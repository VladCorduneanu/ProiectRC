import logger
import enum
import socket
import queue
import threading
import frame
import time
import datetime
import functions
import FrameFactory


class States(enum.Enum):
    SENDER = "sender"
    RECEIVER = "receiver"


class FrameTypes(enum.Enum):
    CONNECT = "connect"
    CONNECTED = "connected"
    DATA = "data"
    LAST = "final"
    ACKNOWLEDGE = "ack"


class StateController:

    # Variables
    def __init__(self):
        self.state = States.RECEIVER
        self.receive_buffer = queue.Queue()
        self.transmit_buffer = queue.Queue()
        self.receive_thread: threading.Thread = threading.Thread()
        self.transmit_thread: threading.Thread = threading.Thread()

        self.kill_thread = False
        self.frameFactory = FrameFactory.FrameFactory()

    pass

    # Static instance -> singleton controller

    instance = None

    # Class Methods

    # transfer function -> start transfer from sender interface
    def transfer_function(self):
        logger.Logger.write("Transfer function triggered")

        #   text to transfer
        packList: [] = functions.getPackagesToSend()

        # check if the file was read correctly
        if packList is None:
            return

        # send the connection package from sender to receiver : Type + total number of packages to send
        # 1. create the package
        totalPacks = len(packList)
        connpack = self.frameFactory.getPackage(FrameTypes.CONNECT.value, totalPacks, None, None, None)
        # 2. put the package into buffer
        logger.Logger.write("Sending connection package")

        # instantiate the state for transfer
        isConnecting = 1  # state to connect
        isTransferring = 0  # state to send data packages
        isFinished = 0  # state for finish package
        isWaiting = 0  # state for wait the buffer to be free -> ack need to free space
        isSending = 0  # state for sending a package

        # initialize the timeout with current time -> start a "timer" to resend data
        lastResponse = datetime.datetime.now()

        # initialize the current package to send
        currentPackNumber = 1

        # initialize the current package received
        currentReceivedPack = 0

        # loop to establish connection
        while isConnecting == 1:

            # check if the timer for resend package was not triggered
            if (datetime.datetime.now() - lastResponse).total_seconds() > 5:
                self.transmit_buffer.put(connpack.encode_message())
                logger.Logger.write("Resending connection pack")
                # reset the timer
                lastResponse = datetime.datetime.now()

            # searching in the receive buffer of SENDER if the connection was established
            if not self.receive_buffer.empty():

                # get the package stored in buffer
                data = self.receive_buffer.get()

                # create and decode the data
                pachet = frame.Frame()
                pachet.decode_message(data)

                # check if it is ACKNOWLEDGE TYPE for connected: Type + Window size
                if pachet.type == 5:
                    # update the timer -> ack before expiring the timer will always reset it: responsive app
                    lastResponse = datetime.datetime.now()

                    # setting transfer window size
                    windowDim = pachet.window_size

                    # change state, if connection succeed:
                    isConnecting = 0  # -> establish connection end
                    isTransferring = 1  # -> starting transfer
                    isSending = 1  # -> starting the sending state
                    isWaiting = 0  # -> initialize the state for waiting to 0

        logger.Logger.write("Connection was established")
        logger.Logger.write("Current sliding window size: " + windowDim.__str__())

        logger.Logger.write("File transfer triggered")
        # loop to transfer the file
        while isTransferring == 1:

            # initialize the current buffer
            buffer_size = currentPackNumber - currentReceivedPack

            # -> check if it is space to load packages in send buffer of SENDER or the file was successful transferred
            if buffer_size - 1 >= windowDim or currentPackNumber > len(packList):
                isSending = 0  # -> stop sending
                isWaiting = 1  # -> wait for an ack

            # state for sending a package
            if isSending == 1:

                # create the package
                packToSend = self.frameFactory.getPackage(FrameTypes.DATA.value, None, None, currentPackNumber,
                                                          packList[currentPackNumber - 1])

                # transmit the package
                self.transmit_buffer.put(packToSend.encode_message())
                logger.Logger.write("Send package: " + currentPackNumber.__str__())

                # increment the next package to send
                currentPackNumber = currentPackNumber + 1

                # check if any package arrived
                if not self.receive_buffer.empty():

                    # reset the timer
                    lastResponse = datetime.datetime.now()

                    # create and decode the message
                    data = self.receive_buffer.get()
                    ackPack = frame.Frame()
                    ackPack.decode_message(data)

                    # chef if the package has ack type
                    if ackPack.type == 5:
                        # update the current received pack
                        currentReceivedPack = ackPack.frame_number
                        logger.Logger.write("Received package: " + currentReceivedPack.__str__())

                        # update the windows size in case of overwhelming
                        windowDim = ackPack.window_size
                        logger.Logger.write("Current sliding window size: " + windowDim.__str__())

            # check if the transfer was not done yet
            if currentReceivedPack == len(packList):
                isTransferring = 0  # -> stop transferring
                isFinished = 1  # -> start finish procedure

            # waiting state triggered by a full buffer -> the send buffer of SENDER is full
            if isWaiting == 1:

                # check if it is any package in the receive buffer of SENDER
                if not self.receive_buffer.empty():

                    # reset timer
                    lastResponse = datetime.datetime.now()

                    # create and decode the message
                    data = self.receive_buffer.get()
                    ackPack = frame.Frame()
                    ackPack.decode_message(data)

                    # check if the package is ack -> resend package if it free space on buffer
                    if ackPack.type == 5:
                        # update the current received pack
                        currentReceivedPack = ackPack.frame_number
                        logger.Logger.write("Received package: " + currentReceivedPack.__str__())

                        # update the windows size in case of overwhelming
                        windowDim = ackPack.window_size
                        logger.Logger.write("Current sliding window size: " + windowDim.__str__())
                        isSending = 1  # the buffer has space -> send another package
                        isWaiting = 0  # the waiting state is done

                # check if the buffer is clear
                else:

                    # if the sender has not any ack from receiver -> trigger the timer to resend
                    if (datetime.datetime.now() - lastResponse).total_seconds() > 15:
                        # reset timer
                        lastResponse = datetime.datetime.now()
                        logger.Logger.write("TIMEOUT triggered -> resend packages")
                        # change the states
                        isWaiting = 0  # stop waiting state
                        isSending = 1  # start resend

                        # the package that need to be resend
                        currentPackNumber = currentReceivedPack + 1
                        logger.Logger.write("Resend from package: " + currentReceivedPack.__str__())

        # the end state was triggered
        while isFinished == 1:
            # create and send the end package
            endPack = self.frameFactory.getPackage(FrameTypes.LAST.value, None, None, None, None)
            self.transmit_buffer.put(endPack.encode_message())
            logger.Logger.write("Send END package: ")

            # stop the transfer
            isFinished = 0

    pass

    # transfer function -> start transfer from receiver interface
    def receive_function(self):
        logger.Logger.write("Receive function triggered ")

        # initialize the list with all decoded messages
        receivedPackList = []

        # states for receiving the file
        isListening = 1  # -> state for establish the connection with sender
        isReceving = 0  # -> state for start receiving data packages
        isFinished = 0  # -> state for finished transaction
        isWaiting = 0  # -> state for waiting packages
        isSendingAck = 0  # -> state for confirm the package

        # initialize the number of package to receive
        length = 0

        # initialize the number of package received
        currentPack = 1

        # initialize the dimension of window
        windowDim = 5

        # loop state for connecting to sender
        while isListening == 1:

            # check if there are any packages in receive buffer of RECEIVER
            if not self.receive_buffer.empty():

                # create and decode the package
                data = self.receive_buffer.get()
                connPack = frame.Frame()
                connPack.decode_message(data)

                # check if it is connection pack
                if connPack.type == 1:
                    # get the total number of packages
                    length = connPack.total_number
                    logger.Logger.write("Connection pack from Sender received ")

                    # create and send ack pack to confirm connection to sender
                    accConnPack = self.frameFactory.getPackage(FrameTypes.ACKNOWLEDGE.value, None, windowDim, 0, None)
                    self.transmit_buffer.put(accConnPack.encode_message())

                    logger.Logger.write("Sending ack to SENDER")
                    # change state
                    isListening = 0  # -> connection to SENDER established
                    isReceving = 1  # -> receiving state triggered
                    isWaiting = 1  # -> waiting for message started
                    isSendingAck = 0  # confirm state set to stop

        logger.Logger.write("Connection to sender established")
        logger.Logger.write("Packages to send: " + length.__str__())

        # loop state for receiving data file messages
        while isReceving == 1:

            # waiting the information package
            if isWaiting == 1:

                # check if it something in receive buffer of RECEIVER
                if not self.receive_buffer.empty():

                    # create amd decode the message
                    data = self.receive_buffer.get()
                    receivedPack = frame.Frame()
                    receivedPack.decode_message(data)

                    # check package type and correct number of frame
                    if receivedPack.type == 3 and currentPack == receivedPack.frame_number:

                        # add package to decoded messages list
                        receivedPackList.append(receivedPack.data)

                        logger.Logger.write("Received package: " + currentPack.__str__())

                        # update the current package
                        currentPack = currentPack + 1

                        # get the current time before the processing the package
                        currentTime = datetime.datetime.now()

                        # generate processing time
                        processTime = functions.genTp()
                        logger.Logger.write("Process the package")

                        # processing
                        time.sleep(processTime)

                        # calculate the time of processing to see if receiver is overwhelmed
                        elapsedTime = (datetime.datetime.now() - currentTime).total_seconds()

                        # update the window size corresponding to elapsesTime
                        windowDim = functions.genWindow(elapsedTime)

                        # change the state after processing to ack the sender
                        isWaiting = 0  # -> stop the waiting state
                        isSendingAck = 1  # -> send ack for current package

                    # check if the received pack was a final pack or the receiver get all the packages
                    elif receivedPack.type == 4 or length == currentPack - 1:

                        # changes state
                        isReceving = 0  # -> stop receiving
                        isFinished = 1  # -> go to finish state
                        isSendingAck = 1  # -> send ack for last package

                    # in case of lost package resend the ack for last good package received
                    else:
                        isWaiting = 0  # -> stop waiting
                        isSendingAck = 1  # -> send ack for last correct package received

            # generating ack for current package
            if isSendingAck == 1:
                # create and send ack package
                ackPack = self.frameFactory.getPackage(FrameTypes.ACKNOWLEDGE.value,
                                                       None, windowDim, currentPack - 1, None)
                self.transmit_buffer.put(ackPack.encode_message())
                logger.Logger.write("Sending ACK for package: " + (currentPack - 1).__str__())

                # change state
                isSendingAck = 0  # stop sending ack
                isWaiting = 1  # -> wait for next package

        # state for finishing transfer
        while isFinished == 1:

            # check if the transfer was successful
            if length == currentPack - 1:
                logger.Logger.write("Transfer Succeed")
            else:
                logger.Logger.write("Transfer failed")

            logger.Logger.write("Decoded messages")
            for it in receivedPackList:
                logger.Logger.write(it)

            # change state -> transfer finished
            isFinished = 0

    pass

    def set_state(self, state):
        # Setting the controller state
        if state == "sender":
            self.state = States.SENDER
        else:
            self.state = States.RECEIVER

        # Starting the thread that will receive messages from the other instance
        argument = "receive"
        self.receive_thread = threading.Thread(target=self.thread_starter, kwargs=dict(mode=argument))
        self.receive_thread.start()

        # Starting the thread that will send messages to the other instance
        argument = "transmit"
        self.transmit_thread = threading.Thread(target=self.thread_starter, kwargs=dict(mode=argument))
        self.transmit_thread.start()

    pass

    # UDP layer for sending messages
    def sender(self):
        # Setting localhost IP
        UDP_IP = "127.0.0.1"

        if self.state == States.RECEIVER:
            UDP_PORT = 5005  # Port Receiver-Sender
        else:
            UDP_PORT = 5006  # Port Sender-Receiver

        # Configuring socket for UDP transmission
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP

        # Main loop for module
        while not self.kill_thread:

            if not self.transmit_buffer.empty():
                MESSAGE: str = self.transmit_buffer.get()

                # Simulating the loss of packages argument being the chance of loss in %
                lost = functions.getLost(10)

                if not lost:
                    # Sending the package
                    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
                else:
                    # Giving log about loss of package
                    ackPack = frame.Frame()
                    ackPack.decode_message(MESSAGE)
                    logger.Logger.write("Package lost: " + "type: " + ackPack.type.__str__() + " number: "
                                        + ackPack.frame_number.__str__())

        sock.close()

    pass

    # UDP layer for receiving messages
    def receiver(self):
        if self.state == States.RECEIVER:
            UDP_PORT = 5006  # Port Sender-Receiver
        else:
            UDP_PORT = 5005  # Port Receiver-Sender

        # Configuring socket for UDP
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind(('', UDP_PORT))

        while not self.kill_thread:
            data = sock.recv(100)  # Maximum size of package in bytes
            self.receive_buffer.put(data.decode())
        sock.close()

    pass

    def close_app(self):
        # Killing receive thread
        if StateController.get_instance().receive_thread:
            StateController.get_instance().kill_thread = True
            if self.state == States.RECEIVER:
                UDP_PORT = 5006
            else:
                UDP_PORT = 5005

            sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
            sock.bind(('', 5007))
            # Sending pack to take the receive thread from waiting and letting the thread kill itself
            string = "closing"
            UDP_IP = "127.0.0.1"
            sock.sendto(string.encode(), (UDP_IP, UDP_PORT))

            sock.close()

        # Killing transmit thread(non blocking functions, only setting the variable)
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
