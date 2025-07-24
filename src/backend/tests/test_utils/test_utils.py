import uuid
import json
import os
from src.backend.run.PipelineRunner import PipelineRunner
from src.backend.types.pipeline import Pipeline
from src.backend.types.frontendNotifier import DummyNotifier
from src.backend.types.blueprint import StepValues
from src.backend.operations.DataPreparationOperation import DataPreparationOperation
from src.backend.operations.KeywordExtractionOperation import KeywordExtractionOperation
from src.backend.operations.SentimentAnalysisOperation import SentimentAnalysisOperation
from src.backend.operations.TextSimilarityOperation import TextSimilarityAnalysisOperation
from src.backend.operations.WordListScanOperation import WordListScanOperation
from src.backend.operations.BertTopic import BertTopicOperation

from src.backend.types.payload import Payload

OPERATION_MAP = {
    "DataPreparationOperation": DataPreparationOperation,
    "KeywordExtractionOperation": KeywordExtractionOperation,
    "SentimentAnalysisOperation": SentimentAnalysisOperation,
    "TextSimilarityOperation": TextSimilarityAnalysisOperation,
    "WordListScanOperation": WordListScanOperation,
    "BertTopic": BertTopicOperation,
}

def load_test_config(config_name: str):
    """Loads a test configuration from a JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "test_configs", config_name)
    with open(config_path, 'r') as f:
        return json.load(f)

def build_pipeline_from_config(config: dict) -> PipelineRunner:
    """Builds a PipelineRunner from a test configuration."""
    operation_name = config["operation_name"]
    operation_class = OPERATION_MAP.get(operation_name)
    if not operation_class:
        raise ValueError(f"Unknown operation: {operation_name}")

    # Create dummy Config and Notifier for testing
    class DummyConfig(dict):
        def get(self, key, default=None):
            return super().get(key, default)

        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    dummy_config = DummyConfig(config["configuration"])
    if "text_column" in config["configuration"]:
        dummy_config["input column"] = config["configuration"]["text_column"]
    dummy_notifier = DummyNotifier()

    operation_instance = operation_class(dummy_config, dummy_notifier)

    # Create a dummy pipeline with a single step
    pipeline = Pipeline(
        id=str(uuid.uuid4()),
        name=config["test_name"],
        description="Test pipeline",
        steps=[
            StepValues(
                    uniqueId=str(uuid.uuid4()),
                    stepId=operation_name,
                    values=config["configuration"]
                )
        ]
    )
    
    return runner

def run_operation_test(config_name: str):
    """Loads config, builds pipeline, runs it, and returns output."""
    config = load_test_config(config_name)
    
    # Create dummy Config and Notifier for testing
    class DummyConfig(dict):
        def get(self, key, default=None):
            return super().get(key, default)

        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    dummy_config = DummyConfig(config["configuration"])
    if "text_column" in config["configuration"]:
        dummy_config["input column"] = config["configuration"]["text_column"]
    dummy_notifier = DummyNotifier()

    operation_instance = OPERATION_MAP.get(config["operation_name"])(dummy_config, dummy_notifier)
    
    # Assuming the input data is for the first (and only) step
    input_data = config["input_data"]
    
    # The run method of operations expects a list of dictionaries
    # where each dictionary is a row of data.
    import pandas as pd
    payload = Payload()
    payload.data = pd.DataFrame(input_data)
    output_data = operation_instance.run(payload, dummy_notifier)
    
    # Extract only the relevant output columns
    processed_data = payload.data.to_dict('records')
    
    # Get the output column name from the configuration
    output_column_name = config["configuration"].get("output column", "similarity")
    
    cleaned_output = []
    for row in processed_data:
        cleaned_output.append({output_column_name: row.get(output_column_name)})

    return cleaned_output, config["expected_output"]
