import enum
from enum import Enum
from typing import List


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

        return _HIERARCHY.get(level, -1)

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
        return _PREFIXES.get(level, "")


class StepState(Enum):
    NOT_STARTED = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3


class NotificationDomain:
    def __init__(self, runId, pipelineId, stepIndex):
        self.runId = runId
        self.pipelineId = pipelineId
        self.stepIndex = stepIndex

    def to_json(self):
        return {
            "runId": self.runId,
            "pipelineId": self.pipelineId,
            "stepIndex": self.stepIndex
        }


class StepStatus:
    def __init__(self, domain: NotificationDomain, state: StepState, progress: float = 0.0):
        self.domain = domain
        self.state = state
        self.progress = progress

    def to_json(self):
        return {
            "domain": self.domain.to_json(),
            "state": self.state.value,
            "progress": self.progress
        }


class Log:

    def __init__(self, level: LogLevels, message: str):
        self.level = level
        self.message = message

    def to_json(self):
        return {
            "level": self.level.value,
            "message": self.message
        }


class StepLogUpdate:
    def __init__(self, domain: NotificationDomain, logs: List[Log]):
        self.domain = domain
        self.logs = logs

    def to_json(self):
        return {
            "domain": self.domain.to_json(),
            "logs": [log.to_json() for log in self.logs]
        }
