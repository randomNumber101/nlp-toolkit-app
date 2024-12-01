from enum import Enum
from typing import List


class StepState(Enum):
    NOT_STARTED = 0,
    RUNNING = 1,
    SUCCESS = 2,
    FAILED = 3


class NotificationDomain:
    def __init__(self, runId, pipelineId, stepIndex):
        self.runId = runId
        self.pipelineId = pipelineId
        self.stepIndex = stepIndex


class StepStatus:
    def __init__(self, domain: NotificationDomain, state: StepState, progress: float = 0.0):
        self.domain = domain
        self.state = state
        self.progress = progress

    def to_json(self):
        return {
            "runId": self.domain.runId,
            "pipelineId": self.domain.pipelineId,
            "stepIndex": self.domain.stepIndex,
            "state": self.state.value,
            "progress": self.progress
        }


class StepLogUpdate:
    def __init__(self, domain: NotificationDomain, logs: List[str]):
        self.domain = domain
        self.logs = logs

    def to_json(self):
        return {
            "runId": self.domain.runId,
            "pipelineId": self.domain.pipelineId,
            "stepIndex": self.domain.stepIndex,
            "logs": self.logs
        }
