from abc import abstractmethod
from typing import List


class LogLevels:
    DEBUG = "Debug | "
    INFO = "INFO | "
    WARN = "WARN | "
    ERROR = "ERROR | "

    HIERARCHY = {
        DEBUG: 0,
        INFO: 1,
        WARN: 2,
        ERROR: 3
    }

    @staticmethod
    def level_of(level):
        if level in LogLevels.HIERARCHY:
            return LogLevels.HIERARCHY[level]
        return -1

    @staticmethod
    def geq(level_0, level_1):
        return LogLevels.level_of(level_0) >= LogLevels.level_of(level_1)


class LoggerChannel:

    @abstractmethod
    def write(self, messages: List[str]):
        pass


class ConsoleLoggerChannel:

    def write(self, message, level):
        print(level + message)


class LogManager:

    def __init__(self, channels=None, log_level=LogLevels.DEBUG):
        self.log_level = log_level
        self.channels = channels if channels is not None else [ConsoleLoggerChannel()]

    def log(self, message, level=LogLevels.INFO):
        if not LogLevels.geq(level, self.log_level):
            return

        for channel in self.channels:
            channel.write(message, level)


    def __call__(self, *args, **kwargs):
        return self.log(*args, **kwargs)
