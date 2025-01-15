from abc import ABC, abstractmethod
from typing import List, Dict, TypeVar, Generic, Optional, Union
from backend.transferObjects.eventTransferObjects import StepStatus, LogLevels



# Define a generic type variable
T = TypeVar("T")


# Define the generic Channel interface
class Channel(ABC, Generic[T]):
    @abstractmethod
    def handle(self, obj: T):
        pass


# Define the generic Multiplexer base class
class Multiplexer(Generic[T], ABC):
    def __init__(self, channels: Optional[Dict[str, Channel[T]]] = None):
        self.channels: Dict[str, Channel[T]] = channels if channels is not None else {}

    def get_channel(self, name: str) -> Optional[Channel[T]]:
        return self.channels.get(name)

    def set_channel(self, name: str, channel: Channel[T]):
        self.channels[name] = channel

    def multiplex(self, obj: T):
        for channel in self.channels.values():
            channel.handle(obj)

    # Allow the multiplexer to be called directly
    def __call__(self, obj: T):
        self.multiplex(obj)


# Refactor LoggerChannel to implement Channel for logging
class LoggerChannel(Channel[Dict[str, Union[str, LogLevels]]]):
    def handle(self, obj: Dict[str, Union[str, LogLevels]]):
        messages: List[str] = obj.get("messages", [])
        level: LogLevels = obj.get("level", LogLevels.INFO)
        for message in messages:
            print(LogLevels.prefix(level) + message)


class LogManager(Multiplexer[Dict[str, Union[str, LogLevels]]]):
    def __init__(self, channels: Optional[Dict[str, Channel[Dict[str, Union[str, LogLevels]]]]] = None, log_level: LogLevels = LogLevels.DEBUG):
        super().__init__(channels if channels is not None else {"console": LoggerChannel()})
        self.log_level = log_level

    def log(self, message: Union[str, List[str]], level: LogLevels = LogLevels.INFO):
        if not LogLevels.geq(level, self.log_level):
            return

        if isinstance(message, str):
            message = message.split("\n")

        log_entry = {"messages": message, "level": level}
        self.multiplex(log_entry)

    # Allow LogManager to be called directly
    def __call__(self, message: Union[str, List[str]], level: LogLevels = LogLevels.INFO):
        self.log(message, level)


# Example implementation of a StatusChannel
class StatusChannel(Channel[StepStatus]):
    def handle(self, status: StepStatus):
        # Print to console
        print(f"Status received: {status.to_json()}")


# Implement the StatusManager by inheriting from Multiplexer
class StatusManager(Multiplexer[StepStatus]):
    def __init__(self, channels: Optional[Dict[str, Channel[StepStatus]]] = None):
        super().__init__(channels if channels is not None else {"default": StatusChannel()})


    def send_status(self, status: StepStatus):
        self.multiplex(status)

    # Allow StatusManager to be called directly
    def __call__(self, status: StepStatus):
        self.send_status(status)
