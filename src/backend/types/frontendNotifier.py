from abc import ABC, abstractmethod
from collections import Counter
from typing import List

from backend.transferObjects.eventTransferObjects import LogLevels, StepState


class FrontendNotifier(ABC):
    @abstractmethod
    def log(self, message: str | List[str], level: LogLevels = LogLevels.DEBUG):
        pass

    @abstractmethod
    def sendStatus(self, stepState: StepState, progress: float = 0.0):
        pass


class CellNotifierWrapper(FrontendNotifier):

    def __init__(self, cellNotifier: FrontendNotifier, successCounter: Counter, cell_index: int,
                 total_cells: int):
        self.cellNotifier = cellNotifier
        self.cell_index = cell_index
        self.total_cells = total_cells
        self.counter = successCounter

    def log(self, message: str | List[str], level: LogLevels = LogLevels.DEBUG):
        prefix = f"Cell {self.cell_index}/{self.total_cells}:"
        if isinstance(message, str):
            message = prefix + message
        else:
            message = [prefix + m for m in message]
        return self.cellNotifier.log(message, level)

    def sendStatus(self, stepState: StepState, progress: float = 0.0):
        if stepState == StepState.SUCCESS:
            self.counter.update("success")
        elif stepState == StepState.FAILED:
            self.counter.update("failed")

        relative_progress = (100 * self.cell_index + progress) / self.total_cells
        self.cellNotifier.sendStatus(StepState.RUNNING, relative_progress)