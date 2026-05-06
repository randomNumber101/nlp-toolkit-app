from src.backend.core.register import GlobalRegistry
import json
import os
from threading import Event
from collections import Counter
from unittest.mock import MagicMock
import pandas as pd
from src.backend.core.Api import Api
from src.backend.run.backendEventApi import BackendEventApi
from src.backend.types.payload import Payload
from src.backend.types.frontendNotifier import FrontendNotifier
from src.backend.transferObjects.eventTransferObjects import StepState


class MockBackendEventApi(BackendEventApi):
    def __init__(self, counters, completion_event: Event):
        self.counters = counters
        self.completion_event = completion_event

    def sendStepStatus(self, status):
        print(f"Status received: {status.state} (progress: {status.progress}%)")
        self.counters[status.state] += 1
        # Only set completion event if it's a final pipeline status (not an intermediate step status)
        if status.domain.stepIndex == 0 and status.state in [StepState.SUCCESS, StepState.FAILED]:
            print("Setting completion event for state: ", status.state)
            self.completion_event.set()

    def sendStepLogs(self, stepLogs):
        pass


def get_mock_backend_event_api():
    api = Api(GlobalRegistry)
    stateCounter = Counter()
    completion_event = Event()
    api.RUNS._eventApi = MockBackendEventApi(stateCounter, completion_event)
    return api, stateCounter, completion_event


class OperationTest:
    def __init__(self, operation_class, config_name: str):
        self.operation_class = operation_class
        self.config = self._load_test_config(config_name)
        self.final_state, self.payload, self.notifier = self._run_operation()

    def _load_test_config(self, config_name: str) -> dict:
        """Loads a test configuration from a JSON file."""
        config_path = os.path.join(os.path.dirname(__file__), "configs", f"{config_name}.json")
        with open(config_path, "r") as f:
            return json.load(f)

    def _run_operation(self):
        """
        Instantiates and runs an operation with the given test configuration.
        Returns the final payload and the mock notifier.
        """
        input_data = self.config["input_data"]
        config_params = self.config["config_params"]

        mock_notifier = MagicMock(spec=FrontendNotifier)

        class MockConfig(dict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for k, v in self.items():
                    if isinstance(v, dict):
                        self[k] = MockConfig(v)
                self.__dict__ = self

            def get_values(self):
                return self

        operation_config = MockConfig(config_params)

        operation_instance = self.operation_class(operation_config, mock_notifier)
        operation_instance.initialize(operation_config, mock_notifier)

        if input_data["type"] == "text":
            df = pd.DataFrame({"text": [input_data["data"]]})
        else:
            df = pd.DataFrame()

        payload = Payload({"data": df})
        payload.addVisualization = MagicMock()

        final_state = operation_instance.run(payload, mock_notifier)

        return final_state, payload.data.to_dict(orient='records'), mock_notifier
