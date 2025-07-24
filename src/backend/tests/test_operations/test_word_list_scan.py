
import pytest
from src.backend.operations.WordListScanOperation import WordListScanOperation
from src.backend.tests.test_utils_operations import OperationTest
from src.backend.transferObjects.eventTransferObjects import StepState


def test_word_list_scan_basic():
    # Arrange
    test = OperationTest(WordListScanOperation, "word_list_scan_basic")

    # Act
    final_state = test.final_state
    payload = test.payload
    config = test.config

    # Assert
    assert final_state.value == StepState.SUCCESS.value
    assert payload # Check if the list is not empty
    assert "test_list" in payload[0]
