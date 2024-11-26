from enum import Enum
from typing import List


class StepState(Enum):
    NOT_STARTED = 0,
    RUNNING = 1,
    SUCCESS = 2,
    FAILED = 3


class StepStatus:
    def __init__(self, runId: str, pipelineId: str, stepIndex: int, state: StepState, progress: float = 0.0):
        self.runId = runId
        self.pipelineId = pipelineId
        self.stepIndex = stepIndex
        self.state = state
        self.progress = progress

    def to_json(self):
        return {
            "runId": self.runId,
            "pipelineId": self.pipelineId,
            "stepIndex": self.stepIndex,
            "state": self.state.value,
            "progress": self.progress
        }


class StepLogUpdate:

    def __init__(self, runId: str, pipelineId: str, stepIndex: int, logs: List[str]):
        self.runId = runId
        self.pipelineId = pipelineId
        self.stepIndex = stepIndex
        self.logs = logs

    def to_json(self):
        return {
            "runId": self.runId,
            "pipelineId": self.pipelineId,
            "stepIndex": self.stepIndex,
            "logs": self.logs
        }
