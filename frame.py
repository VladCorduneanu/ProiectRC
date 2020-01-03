class Frame:
    def __init__(self):
        self.type: int = 0
        self.length: int = 0
        self.window_size = 0
        self.data: str = ""
        self.frame_number: int = 0
        self.total_number: int = 0

    pass

    # EOF = >
    # SOF = <
    # escape = /
    # special ch for spacing = +
    # end of transmission = ~
    # "/" =//   "<"= /<  ">"=/>  "+"=/+

    def encode_message(self):
        message: str = ""
        message = message + "<"
        message = message + self.type.__str__()

        if self.type == 1:
            # connection package with total number of packages to send
            message = message + self.total_number.__str__()
        elif self.type == 3:
            # connection package with information from file
            message = message + "+" + self.frame_number.__str__() + "+" + self.length.__str__() + "+" + self.data
        elif self.type == 4:
            # end connection package
            message = message + "+" + "~"
        elif self.type == 5:
            # ack connection
            message = message + "+" + self.frame_number.__str__() + "+" + self.window_size.__str__()
        else:
            print("Error")
        message = message + ">"
        return message

    def decode_message(self, data):
        if data[0] != "<" and data[len(data) - 1 == ">"]:
            print("bad message " + data)
        self.type = int(data[1])
        if self.type == 1:
            self.total_number = int(data[2:len(data) - 1])
            return
        elif self.type == 2:
            self.window_size = int(data[3:len(data) - 1])
        elif self.type == 3:
            aux = ""
            i = 3
            while data[i] != '+':
                aux = aux + data[i]
                i = i + 1
            self.frame_number = int(aux)
            i = i + 1
            aux = ""
            while data[i] != '+':
                aux = aux + data[i]
                i = i + 1
            self.length = int(aux)

            info = ""
            for j in range(i + 1, i + self.length + 1):
                info = info + data[j]
            flag: bool = False
            for it in info:
                if flag is True:
                    flag = False
                    self.data = self.data + it
                    continue

                if it == '/':
                    flag = True
                    continue

                if it == "+" or it == "<" or it == ">" or it == "~":
                    print("Error -> Characters error")
                    self.type = 0
                    return

                self.data = self.data + it
        elif self.type == 4:
            print("Final package")
        elif self.type == 5:
            aux = ""
            i = 3
            while data[i] != '+':
                aux = aux + data[i]
                i = i + 1
            self.frame_number = int(aux)
            i = i + 1
            aux = ""
            while data[i] != '>':
                aux = aux + data[i]
                i = i + 1
            self.window_size = int(aux)
