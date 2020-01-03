import frame

class PackageFacatory:
    def getPackage(self, type, dim, windowSize, frame_number,data):
        pack = frame.Frame()

        if type == "connect":
            pack.type = 1
            pack.total_number = dim
        elif type == "connected":
            pack.type = 2
            pack.window_size = windowSize
        elif type == "data":
            pack.type = 3
            pack.frame_number = frame_number
            pack.data = data
            pack.length = len(pack.data)
        elif type == "final":
            pack.type = 4
        elif type == "ack":
            pack.type = 5
            pack.frame_number = frame_number
            pack.window_size = windowSize
        return pack
    pass