from datetime import datetime
import os


class Logger:

    # Variables
    def __init__(self):
        self.text = ""

        if os.path.exists("Logs.txt"):
            try:
                os.remove("Logs.txt")
            except IOError:
                print("Logger is used by another process")
        else:
            print("The file does not exist")

        self.file = open("Logs.txt", "a+")
        self.write_to_file()
    pass

    # Static instance

    instance = None

    # Class Methods

    def write_log(self, received_text):
        # datetime object containing current date and time
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S:%f")
        dt_string = "["+dt_string+"]  "
        self.text = self.text+"\n"+dt_string+received_text
        if len(self.text) >= 100:
            self.write_to_file()
        pass

    def write_to_file(self):

        try:
            self.file.write(self.text)
            self.text = ""
        except IOError:
            print("Error: File does not appear to exist.")

    pass

    @staticmethod
    def get_instance():
        if Logger.instance is None:
            Logger.instance = Logger()
        return Logger.instance

    pass

    @staticmethod
    def write(txt):
        Logger.get_instance().write_log(txt)
    pass

    @staticmethod
    def flush():
        Logger.get_instance().write_to_file()
    pass

    @staticmethod
    def on_exit():
        Logger.flush()
        Logger.get_instance().file.close()
    pass
