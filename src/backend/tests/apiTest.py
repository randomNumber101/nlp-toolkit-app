import time
from collections import Counter

from backend.Api import Api
from backend.events.backendEventApi import BackendEventApi
from backend.transferObjects.eventTransferObjects import StepStatus, StepState, StepLogUpdate


def test_get_blueprints():
    api = Api()
    steps = api.STORAGE.load_all_steps()
    assert True


def test_get_pipelines():
    api = Api()
    steps = api.STORAGE.load_all_pipelines()
    assert True


def test_run_pipeline():
    api = Api()
    pipeline = api.STORAGE.PIPELINES.load_all()[0]

    stateCounter = Counter()

    class MockBackendEventApi(BackendEventApi):

        def __init__(self, counters):
            self.counters = counters

        def sendStepStatus(self, status: StepStatus):
            self.counters[status.state] += 1
            print(f"Sent status {status.state} ({status.progress}%) to frontend.")

        def sendStepLogs(self, stepLogs: StepLogUpdate):
            print("Sent logs to frontend.")

    api.RUNS.eventApi = MockBackendEventApi(stateCounter)
    api.RUNS.startRun(pipeline.id, "Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")
    time.sleep(3)
    assert stateCounter[StepState.SUCCESS] > 0, "Pipeline did not complete successfully!"
    assert stateCounter[StepState.FAILED] == 0, "Pipeline encountered a failure!"
