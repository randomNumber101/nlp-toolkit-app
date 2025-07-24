import pytest
from unittest.mock import patch, MagicMock
import torch
from src.backend.operations.TextSimilarityOperation import TextSimilarityAnalysisOperation as TextSimilarityOperation
from src.backend.tests.test_utils_operations import OperationTest
from src.backend.transferObjects.eventTransferObjects import StepState

# Mock sklearn to prevent import issues within transformers
import sys
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.cluster'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()

@patch.object(TextSimilarityOperation, 'compute_embedding', return_value=torch.randn(1, 768))
def test_text_similarity_operation(mock_compute_embedding):
    test = OperationTest(TextSimilarityOperation, "text_similarity_basic")
    final_state = test.final_state
    payload = test.payload
    config = test.config

    assert final_state.value == StepState.SUCCESS.value
    assert payload # Check if the list is not empty
    assert "similarity" in payload[0]