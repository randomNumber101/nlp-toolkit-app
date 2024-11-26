import uuid
from abc import ABC, abstractmethod
from typing import Dict, List

from backend.events.eventTransferObjects import StepState
from backend.parameterTypes import Parameter, InputOutputDefinition

from pandas import DataFrame
import pandas as pd

from backend.run.LogManager import LogLevels


# Might be specified later
class Input(DataFrame):
    pass

    @staticmethod
    def from_csv(file_or_buffer) -> 'Input':
        return Input(pd.read_csv(file_or_buffer))


class Payload(Dict[str, object]):

    def __init__(self, values: Dict = None, link_to_parent: Dict = None):
        self.protected_names = {"original_data", "data", "visualizations"}
        if values is not None:
            for k, v in values.items():
                if k not in self.protected_names:
                    self.k = v
        super().__init__()

    def __setitem__(self, key, value):
        if self.link_to_parent is not None:
            self.link_to_parent[key] = value
        return super().__setitem__(key, value)

    def __getitem__(self, key):
        if self.link_to_parent is not None:
            return self.link_to_parent[key]
        return super().__getitem__(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        if self.link_to_parent is not None and key not in self and key in self.link_to_parent:
            raise ValueError(
                f"{key} is not in this partial view, but in parent. You might have forgotten to declare it as input.")

        return self[key]

    def partialView(self, params: List[Parameter]):
        return Payload(
            {
                param.name: param.type.parse(self[param.name]) for param in params
            }, link_to_parent=self
        )


class FrontendNotifier(ABC):
    @abstractmethod
    def log(self, message: str | List[str], level: LogLevels = LogLevels.DEBUG):
        pass

    @abstractmethod
    def sendStatus(self, stepState: StepState, progress: float):
        pass


class StepOperation(ABC):
    def __init__(self, stepId, logger):
        self.logger = logger
        self.stepId = stepId

    @abstractmethod
    def run(self, payload, notifier: FrontendNotifier):
        pass

    def __call__(self, payload, notifier: FrontendNotifier):
        self.run(payload, notifier)


class StepOperationMapper:

    def __init__(self):
        self.operations = {}

    def registerOperation(self, operation: StepOperation):
        self.operations[operation.stepId] = operation

    def getOperation(self, stepId):
        if stepId in self.operations:
            return self.operations[stepId]
        raise NotImplementedError(
            f"No registered operation found for Step Id {stepId}. Create new or register operation.")


class StepBlueprint:
    def __init__(self, stepId, name, operation: StepOperation, description, inOutDef: InputOutputDefinition):
        self.stepId = stepId
        self.name = name
        self.operation = operation
        self.description = description
        self.inOutDef = inOutDef

    def satisfiesStatic(self, values: dict[str, object]):
        pass

    def __call__(self, payload, params):
        inputs = payload.partialView(params)
        self.operation(inputs)
        return payload


class StepValues:
    def __init__(self, stepId: str, values: Dict[str, object]):
        self.stepId = stepId
        self.values = values


class Pipeline:
    def __init__(self, id, name, description="", steps: List[StepValues] = None):
        self.id = id
        self.name = name
        self.description = description
        if steps is None:
            steps = []
        self.steps = steps
