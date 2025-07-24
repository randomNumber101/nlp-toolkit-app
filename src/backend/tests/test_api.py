import time
from collections import Counter
from unittest.mock import patch, MagicMock

from backend.Api import Api
from src.backend.tests.test_utils_operations import get_mock_backend_event_api

def build_input_handle(text):
    return {
        "data": text,
        "type": "text"
    }
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
    api, state_counter, completion_event = get_mock_backend_event_api()
    pipeline = api.STORAGE.PIPELINES.load_all()[0]
    num_steps = len(pipeline.steps)

    input_handle = build_input_handle("Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")
    run_id = api.RUNS.startRun(pipeline.id, input_handle)
    
    time.sleep(10) # Give pipeline some time to process

    assert state_counter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert state_counter[StepState.FAILED] == 0, "Pipeline encountered a failure!"

    df = api.RUNS._runStorageApi.getResult(run_id)
    assert df is not None and not df.empty, "No result was saved."


@patch('backend.operations.DataPreparationOperation.load_spacy_model_on_demand', return_value=MagicMock())
def test_run_data_prep_op(mock_load_spacy_model):
    api, state_counter, completion_event = get_mock_backend_event_api()
    pipes = api.STORAGE.PIPELINES.load_all()
    operation_pipe = None
    for pipe in pipes:
        if "DataPreparation" in pipe.id:
            operation_pipe = pipe
            break

    input_handle = build_input_handle("Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")

    api.RUNS.startRun(operation_pipe.id, input_handle)
    
    time.sleep(10) # Give pipeline some time to process
    num_steps = len(operation_pipe.steps)
    assert state_counter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert state_counter[StepState.FAILED] == 0, "Pipeline encountered a failure!"


@patch('hdbscan.HDBSCAN', return_value=MagicMock())
@patch('sklearn.cluster.HDBSCAN', return_value=MagicMock())
def test_run_berttopic_op(mock_hdbscan, mock_sklearn_hdbscan):
    api, state_counter, completion_event = get_mock_backend_event_api()
    pipes = api.STORAGE.PIPELINES.load_all()
    operation_pipe = None
    for pipe in pipes:
        if "BertTopic" in pipe.id:
            operation_pipe = pipe
            break

    input_handle = build_input_handle("Lorem ipsum dolomit lorem quantum sit. No kunor sic honem dores isef.")

    api.RUNS.startRun(operation_pipe.id, input_handle)
    
    time.sleep(10) # Give pipeline some time to process

    num_steps = len(operation_pipe.steps)
    assert state_counter[StepState.SUCCESS] >= num_steps, "Pipeline did not complete successfully!"
    assert state_counter[StepState.FAILED] == 0, "Pipeline encountered a failure!"
