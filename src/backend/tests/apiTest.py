import time
from collections import Counter

from backend.Api import Api
from backend.tests.utils import get_mock_backend_event_api, build_input_handle
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
    api, stateCounter = get_mock_backend_event_api()
    pipeline = api.STORAGE.PIPELINES.load_all()[0]
    num_steps = len(pipeline.steps)

    run_id = api.RUNS.startRun(pipeline.id, "Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")
    time.sleep(8)  # Wait for run to end. Could also dynamically check via the progress status.
    assert stateCounter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert stateCounter[StepState.FAILED] == 0, "Pipeline encountered a failure!"

    df = api.RUNS.runStorageApi.getResult(run_id)
    assert df is not None and not df.empty, "No result was saved."


def test_run_word_lists_op():
    api, stateCounter = get_mock_backend_event_api()
    pipes = api.STORAGE.PIPELINES.load_all()
    operation_pipe = None
    for pipe in pipes:
        if "WordListScan" in pipe.id:
            operation_pipe = pipe
            break

    input = build_input_handle("Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")

    api.RUNS.startRun(operation_pipe.id, input)
    time.sleep(3)  # Wait for run to end. Could also dynamically check via the progress status.
    num_steps = len(operation_pipe.steps)
    assert stateCounter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert stateCounter[StepState.FAILED] == 0, "Pipeline encountered a failure!"


def test_run_data_prep_op():
    api, stateCounter = get_mock_backend_event_api()
    pipes = api.STORAGE.PIPELINES.load_all()
    operation_pipe = None
    for pipe in pipes:
        if "DataPreparation" in pipe.id:
            operation_pipe = pipe
            break

    input = build_input_handle("Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")

    api.RUNS.startRun(operation_pipe.id, input)
    time.sleep(3)  # Wait for run to end. Could also dynamically check via the progress status.
    num_steps = len(operation_pipe.steps)
    assert stateCounter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert stateCounter[StepState.FAILED] == 0, "Pipeline encountered a failure!"


def test_run_berttopic_op():
    api, stateCounter = get_mock_backend_event_api()
    pipes = api.STORAGE.PIPELINES.load_all()
    operation_pipe = None
    for pipe in pipes:
        if "BertTopic" in pipe.id:
            operation_pipe = pipe
            break

    input = build_input_handle("Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")

    api.RUNS.startRun(operation_pipe.id, input)
    time.sleep(100)  # Wait for run to end. Could also dynamically check via the progress status.
    num_steps = len(operation_pipe.steps)
    assert stateCounter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert stateCounter[StepState.FAILED] == 0, "Pipeline encountered a failure!"
