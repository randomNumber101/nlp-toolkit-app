from src.backend.tests.test_utils_operations import OperationTest
from src.backend.operations.DataPreparationOperation import DataPreparationOperation
from src.backend.transferObjects.eventTransferObjects import StepState

def test_data_preparation_operation():
    test = OperationTest(DataPreparationOperation, "data_preparation_basic")
    final_state = test.final_state
    payload = test.payload
    config = test.config

    assert final_state.value == StepState.SUCCESS.value
    assert payload # Check if the list is not empty
    assert payload[0]["text"] == config["expected_output"]["text"]

def test_data_preparation_operation_with_different_config():
    test = OperationTest(DataPreparationOperation, "data_preparation_basic")
    final_state = test.final_state
    payload = test.payload
    config = test.config

    assert final_state.value == StepState.SUCCESS.value
    assert payload # Check if the list is not empty
    assert payload[0]["text"] == config["expected_output"]["text"]
