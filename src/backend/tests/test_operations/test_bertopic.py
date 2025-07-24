
import pytest
from src.backend.operations.BertTopic import BertTopicOperation as BertTopic
from src.backend.tests.test_utils_operations import OperationTest
from src.backend.transferObjects.eventTransferObjects import StepState


def test_bertopic_basic():
    # Arrange
    test = OperationTest(BertTopic, "bertopic_basic")

    # Act
    final_state = test.final_state
    payload = test.payload
    config = test.config

    # Assert
    assert final_state.value == StepState.SUCCESS.value
    assert payload is not None # Check if the list is not empty
    assert "topic_id" in payload[0]
    assert "topic_words" in payload[0]
