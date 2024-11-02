import uuid
from abc import ABC, abstractmethod
from typing import Dict, List
from src.backend.parameterTypes import Parameter, InputOutputDefinition


class Payload(Dict[str, object]):

    def __init__(self, values: Dict = None, link_to_parent: Dict = None):
        if values is not None:
            for k, v in values.items():
                self.k = v
        super().__init__()

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if self.link_to_parent is not None:
            self.link_to_parent[key] = value
        super().__setitem__(key, value)

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

class StepOperation(ABC):
    def __init__(self, stepId):
        self.stepId = stepId
        # Register this in register.py
        from register import Register
        Register.OperationMapper.registerOperation(self)

    @abstractmethod
    def run(self, payload):
        pass

    def __call__(self, payload):
        self.run(payload)


class StepOperationMapper:

    def __init__(self):
        self.operations = {}

    def registerOperation(self, operation: StepOperation):
        self.operations[operation.stepId] = operation

    def getOperation(self, stepId):
        if id in self.operations:
            return self.operations[stepId]
        raise NotImplementedError(f"No registered operation found for Step Id {stepId}. Create new or register operation.")


class StepBlueprint:
    def __init__(self, stepId, name, operation: StepOperation, description, inOutDef: InputOutputDefinition):
        self.stepId = stepId
        self.name = name
        self.operation = operation
        self.description = description
        self.inOutDef = inOutDef

    def __call__(self, payload, params):
        inputs = payload.partialView(params)
        self.operation(inputs)
        return payload


class Pipeline:
    def __init__(self, id=None, name=None, description="", steps: List[StepBlueprint] = None):

        if id is None:
            self.id = uuid.uuid4().hex

        if name is None:
            self.name = f"Pipeline {id}"

        if steps is None:
            steps = []

        self.description = description

    @staticmethod
    def from_config(config):
        return Pipeline()





