from collections import Counter

from backend.Api import Api
from backend.run.backendEventApi import BackendEventApi
from backend.transferObjects.eventTransferObjects import StepStatus, StepLogUpdate


class MockBackendEventApi(BackendEventApi):

    def __init__(self, counters):
        self.counters = counters

    def sendStepStatus(self, status: StepStatus):
        self.counters[status.state] += 1
        print(f"Sent status {status.state} ({status.progress}%) to frontend.")

    def sendStepLogs(self, stepLogs: StepLogUpdate):
        print("Sent logs to frontend.")


def get_mock_backend_event_api():
    api = Api()
    stateCounter = Counter()
    api.RUNS._eventApi = MockBackendEventApi(stateCounter)
    return api, stateCounter


def build_input_handle(text):
    return {
        "data": text,
        "type": "text"
    }
