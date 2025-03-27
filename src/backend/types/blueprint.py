import traceback
from typing import List, Dict

from backend.transferObjects.eventTransferObjects import LogLevels, StepState
from backend.types.config import Config
from backend.types.frontendNotifier import FrontendNotifier
from backend.types.operation import StepOperation
from backend.types.params import Parameter, StaticParameter
from backend.types.payload import Payload


class InputOutputDefinition:
    def __init__(self, staticInputs: List[StaticParameter], dynamicInputs: List[Parameter], outputs: List[Parameter]):
        self.inputs_static = staticInputs
        self.inputs_dynamic = dynamicInputs
        self.outputs = outputs



class StepValues:
    def __init__(self, uniqueId: str, stepId: str, values: Dict[str, object]):
        self.uniqueId = uniqueId
        self.stepId = stepId
        self.values = values


class StepBlueprint:
    def __init__(self, stepId, name, operation: type[StepOperation], description, inOutDef: InputOutputDefinition,
                 information: str = None,
                 tags: List[str] = None):
        self.stepId = stepId
        self.name = name
        self.operation = operation
        self.description = description
        self.information = information
        self.inOutDef = inOutDef
        self.tags = tags if tags else []

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
        try:
            operation_obj = self.operation(config, notifier)
        except Exception as e:
            traceback_str = traceback.format_exc()
            notifier.log(traceback_str, LogLevels.ERROR)
            notifier.log(f"Backend exception during operation initialization: {repr(e)}", LogLevels.ERROR)
            return StepState.FAILED

        # Restrict the payload to only own the values that are relevant for this operation:
        partial_payload = payload.partialView(self.inOutDef.inputs_dynamic)

        # Run operation
        return operation_obj(partial_payload, notifier=notifier)