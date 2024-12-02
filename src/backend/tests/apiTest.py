import time
from collections import Counter

from backend.Api import Api
from backend.events.backendEventApi import BackendEventApi
from backend.transferObjects.eventTransferObjects import StepStatus, StepState, StepLogUpdate


def test_get_blueprints():
    api = Api()
    steps = api.STORAGE.load_all_steps()
    assert len(steps) > 0


def test_get_pipelines():
    api = Api()
    pipes = api.STORAGE.load_all_pipelines()
    assert len(pipes) > 0


def test_run_pipeline():
    api = Api()
    pipeline = api.STORAGE.PIPELINES.load_all()[0]
    num_steps = len(pipeline.steps)

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
    run_id = api.RUNS.startRun(pipeline.id, "Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")
    time.sleep(8)  # Wait for run to end. Could also dynamically check via the progress status.
    assert stateCounter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert stateCounter[StepState.FAILED] == 0, "Pipeline encountered a failure!"

    df = api.RUNS.runStorageApi.getResult(run_id)
    assert df is not None and not df.empty, "No result was saved."
