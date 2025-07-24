import pytest
from src.backend.operations.KeywordExtractionOperation import KeywordExtractionOperation
from src.backend.tests.test_utils_operations import OperationTest
from src.backend.transferObjects.eventTransferObjects import StepState

def test_keyword_extraction_operation():
    test = OperationTest(KeywordExtractionOperation, "keyword_extraction_basic")
    final_state = test.final_state
    payload = test.payload
    config = test.config

    assert final_state.value == StepState.SUCCESS.value
    assert payload # Check if the list is not empty
    assert "keywords" in payload[0]