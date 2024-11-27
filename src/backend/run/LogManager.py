import enum
from abc import abstractmethod
from typing import List, Dict


class LogLevels(enum.Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3

    @staticmethod
    def level_of(level):
        _HIERARCHY = {
            LogLevels.DEBUG: 0,
            LogLevels.INFO: 1,
            LogLevels.WARN: 2,
            LogLevels.ERROR: 3
        }

        if level in _HIERARCHY:
            return _HIERARCHY[level]
        return -1

    @staticmethod
    def geq(level_0, level_1):
        return LogLevels.level_of(level_0) >= LogLevels.level_of(level_1)

    @staticmethod
    def prefix(level):
        _PREFIXES = {
            LogLevels.DEBUG: "DEBUG | ",
            LogLevels.INFO: "INFO | ",
            LogLevels.WARN: "WARN | ",
            LogLevels.ERROR: "ERROR | "
        }
        return _PREFIXES.get(level, default="")


class LoggerChannel:

    @abstractmethod
    def write(self, messages: List[str], level: LogLevels):
        pass


class ConsoleLoggerChannel(LoggerChannel):

    def write(self, messages: List[str], level):
        for message in messages:
            print(LogLevels.prefix(level) + message)


class LogManager:

    def __init__(self, channels: Dict[str, LoggerChannel] = None, log_level=LogLevels.DEBUG):
        self.log_level = log_level
        self.channels = channels if channels is not None else {"console": ConsoleLoggerChannel()}

    def getChannel(self, name):
        return self.channels.get(name, None)

    def setChannel(self, name, channel: LoggerChannel):
        self.channels[name] = channel

    def log(self, message: str | List[str], level=LogLevels.INFO):
        if not LogLevels.geq(level, self.log_level):
            return

        if isinstance(message, str):
            message = [message]

        for _, channel in self.channels.items():
            channel.write(message, level)


    def __call__(self, *args, **kwargs):
        return self.log(*args, **kwargs)
