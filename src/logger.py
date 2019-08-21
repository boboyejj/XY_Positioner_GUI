import logging

#logging.basicConfig(filename="NS Testing.log", level=logging.INFO)

class Log():
    def __init__(self, filename):
        self.filename = filename

    def getLogger(self):
        logger = logging.getLogger('user')
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s:%(message)s", "%H:%M:%S")

        # handle info to a log file
        # file_handler = logging.FileHandler("log/NS Testing.log")
        file_handler = logging.FileHandler(self.filename)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # handle info to the sys.stdout
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        # logger.addHandler(consoleHandler)
        return logger
