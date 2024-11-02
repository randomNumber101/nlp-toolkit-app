class Logger:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3

    def __init__(self, logfile=None, mode=DEBUG):
        self.logfile = logfile
        self.mode = mode
        pass

    def debug(self, message):
        if self.mode > Logger.DEBUG:
            return
        print(f"DEBUG: {message}")

    def info(self, message):
        if self.mode > Logger.INFO:
            return
        print(f"INFO: {message}")

    def warn(self, message):
        if self.mode > Logger.WARN:
            return
        print(f"WARN: {message}")

    def error(self, message):
        if self.mode > Logger.ERROR:
            return
        print(f"ERROR: {message}")


log = Logger()
