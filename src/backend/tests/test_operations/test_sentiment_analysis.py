
import pytest
from src.backend.operations.SentimentAnalysisOperation import SentimentAnalysisOperation
from src.backend.tests.test_utils_operations import OperationTest
from src.backend.transferObjects.eventTransferObjects import StepState


def test_sentiment_analysis_basic():
    # Arrange
    test = OperationTest(SentimentAnalysisOperation, "sentiment_analysis_basic")

    # Act
    final_state = test.final_state
    payload = test.payload
    config = test.config

    # Assert
    assert final_state.value == StepState.SUCCESS.value
    assert payload is not None # Check if the list is not empty
    assert "sentiment_label" in payload[0]
    assert "sentiment_score" in payload[0]
