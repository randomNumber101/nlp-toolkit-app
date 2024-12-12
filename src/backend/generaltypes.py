import copy
import time
import typing
from abc import ABC, abstractmethod
from collections import Counter
from typing import Dict, List, Type, Any, Optional

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.parameterTypes import Parameter, InputOutputDefinition, ComplexType, ParamType

from pandas import DataFrame
import pandas as pd


# Might be specified later
class Input(DataFrame):
    pass

    @staticmethod
    def from_csv(file_or_buffer) -> 'Input':
        return Input(pd.read_csv(file_or_buffer))


class Payload(Dict[str, Any]):

    def __init__(self, values: Optional[Dict[str, Any]] = None, link_to_parent: Optional['Payload'] = None):
        super().__init__()
        self.link_to_parent = link_to_parent

        # Initialize protected attributes
        if not link_to_parent:
            super().__setitem__('visualizations', [])

        if values is not None:
            for k, v in values.items():
                super().__setitem__(k, v)  # Correctly set attribute based on key

    def __setitem__(self, key: str, value: Any):
        if self.link_to_parent is not None:
            self.link_to_parent[key] = value
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        if key == "visualizations" and self.link_to_parent:
            return self.link_to_parent[key]
        if self.link_to_parent and key not in self and key in self.link_to_parent:
            raise ValueError(
                f"{key} is not in this partial view, but in parent. You might have forgotten to declare it as input.")
        return super().__getitem__(key)

    def __setattr__(self, key: str, value: Any):
        if key in {'link_to_parent'}:
            super().__setattr__(key, value)
            return
        self[key] = value

    def __getattr__(self, key: str) -> Any:
        if key in {'link_to_parent'}:
            super().__getattribute__(key)

        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'Payload' object has no attribute '{key}'")

    def popVisualizations(self):
        visualizations = self['visualizations']
        self['visualizations'] = []
        return visualizations

    def addVisualization(self, viz: Any):
        self['visualizations'].append(viz)

    def partialView(self, params: List['Parameter']) -> 'Payload':
        partial_values = {param.name: param.type.parse(self[param.name]) for param in params}
        return Payload(partial_values, link_to_parent=self)


class Config:
    def __init__(self, parameters: List[Parameter]):
        super().__init__()

        self.complexFields = set([])
        self.fields = {}
        for p in parameters:
            if p.type.name == "complex":
                pType = typing.cast(ComplexType, p.type)
                self.fields[p.name] = Config(pType.innerParams)
                self.complexFields.add(p.name)
            else:
                self.fields[p.name] = p

        self.values = {}
        for p in parameters:
            if p.name not in self.complexFields and p.defaultValue is not None:
                self.values[p.name] = self.fields[p.name].type.parse(p.defaultValue)

    def setValues(self, vals: dict[str, object]):
        for vName, vValue in vals.items():
            if vName in self.complexFields:
                complexValues = typing.cast(Dict[str, object], vValue)
                self.fields[vName].setValues(complexValues)
            else:
                self.values[vName] = self.fields[vName].type.parse(vValue)

    def getMissingValues(self) -> typing.Iterable[str]:
        for key in self.fields:
            if key in self.complexFields:
                for missingChildKey in self.fields[key].getMissingValues():
                    yield f"{key}.{missingChildKey}"
            elif key not in self.values:
                yield key

    def isReady(self) -> bool:
        return not any(self.getMissingValues())

    def __getitem__(self, item):
        return self.get(item, None)

    def get(self, item, default=None):
        if item in self.complexFields:
            if item in self.fields:
                return self.fields[item]
            return default
        if item in self.values:
            return self.values[item]
        return default

    def __setitem__(self, key, value):
        self.setValues({key: value})


class FrontendNotifier(ABC):
    @abstractmethod
    def log(self, message: str | List[str], level: LogLevels = LogLevels.DEBUG):
        pass

    @abstractmethod
    def sendStatus(self, stepState: StepState, progress: float = 0.0):
        pass


class StepOperation(ABC):
    def __init__(self, config: Config):
        self.initialize(config)

    @abstractmethod
    def initialize(self, config: Config):
        pass

    @abstractmethod
    def run(self, payload, notifier: FrontendNotifier) -> StepState:
        pass

    def __call__(self, payload, notifier: FrontendNotifier) -> StepState:
        return self.run(payload, notifier)


class CellNotifierWrapper(FrontendNotifier):

    def __init__(self, cellNotifier: FrontendNotifier, successCounter: Counter, cell_index: int,
                 total_cells: int):
        self.cellNotifier = cellNotifier
        self.cell_index = cell_index
        self.total_cells = total_cells
        self.counter = successCounter

    def log(self, message: str | List[str], level: LogLevels = LogLevels.DEBUG):
        prefix = f"Cell {self.cell_index}/{self.total_cells}:"
        if isinstance(message, str):
            message = prefix + message
        else:
            message = [prefix + m for m in message]
        return self.cellNotifier.log(message, level)

    def sendStatus(self, stepState: StepState, progress: float = 0.0):
        if stepState == StepState.SUCCESS:
            self.counter.update("success")
        elif stepState == StepState.FAILED:
            self.counter.update("failed")

        relative_progress = (100 * self.cell_index + progress) / self.total_cells
        self.cellNotifier.sendStatus(StepState.RUNNING, relative_progress)


class ParallelizableTextOperation(StepOperation, ABC):

    def __init__(self, config: Config):
        self.config = config
        self.input_column = self.config.get("input column", "text")
        if isinstance(self.input_column, list):
            self.input_column = self.input_column[0]  # Assuming single column for simplicity

        # Determine the output column
        self.output_column = self.config.get("output column", None)
        if self.output_column == "":
            self.output_column = self.input_column  # Overwrite
        elif self.output_column is None:
            self.output_column = self.input_column  # Default to overwrite if not specified
        super(ParallelizableTextOperation, self).__init__(config)

    @abstractmethod
    def single_cell_operation(self, notifier: FrontendNotifier, payload: Payload, text: str) -> str:
        pass

    def run(self, payload, notifier: FrontendNotifier) -> StepState:
        start_time = time.time()

        data: pd.DataFrame = payload.data

        print(data)

        counter = Counter({"success": 0, "failed": 0})
        cell_index = 0
        num_cells = len(data[self.input_column])

        def transform(text: str):
            nonlocal cell_index
            cellNotifier = CellNotifierWrapper(notifier, counter, cell_index, num_cells)
            cell_index += 1
            self.initialize(self.config)
            return self.single_cell_operation(cellNotifier, payload, text)

        data[self.output_column] = data[self.input_column].apply(transform)
        end_time = time.time()
        notifier.log(f"Total processing time: {end_time - start_time:.2f} seconds", LogLevels.INFO)
        if counter["failed"] > 0:
            notifier.log(f"{counter['failed']} of {num_cells} failed. Data will not be saved.", LogLevels.ERROR)
            return StepState.FAILED

        payload.data = data
        return StepState.SUCCESS


class StepOperationMapper:

    def __init__(self):
        self.operations = {}

    def registerOperation(self, stepId: str, operation: Type[StepOperation]):
        self.operations[stepId] = operation

    def getOperation(self, stepId) -> Type[StepOperation]:
        if stepId in self.operations:
            return self.operations[stepId]
        raise NotImplementedError(
            f"No registered operation found for Step Id {stepId}. Create new or register operation.")


class StepValues:
    def __init__(self, stepId: str, values: Dict[str, object]):
        self.stepId = stepId
        self.values = values


class StepBlueprint:
    def __init__(self, stepId, name, operation: type[StepOperation], description, inOutDef: InputOutputDefinition):
        self.stepId = stepId
        self.name = name
        self.operation = operation
        self.description = description
        self.inOutDef = inOutDef

    def run(self, configValues: StepValues, payload: Payload, notifier: FrontendNotifier):
        config = Config(self.inOutDef.inputs_static)
        config.setValues(configValues.values)
        if not config.isReady():
            missingValues = list(config.getMissingValues())
            notifier.log(f"Config object seems to miss some values: {config.values}")
            notifier.log(f"Cannot run {self.name} due to missing config parameters: {missingValues}",
                         LogLevels.ERROR)
            return StepState.FAILED

        # Create the actual operation instance
        operation_obj = self.operation(config)

        # Restrict the payload to only own the values that are relevant for this operation:
        partial_payload = payload.partialView(self.inOutDef.inputs_dynamic)

        # Run operation
        return operation_obj(partial_payload, notifier=notifier)


class Pipeline:
    def __init__(self, id, name, description="", steps: List[StepValues] = None):
        self.id = id
        self.name = name
        self.description = description
        if steps is None:
            steps = []
        self.steps = steps
