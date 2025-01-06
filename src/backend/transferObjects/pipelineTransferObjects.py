from typing import List, Dict, Optional
import uuid

from backend.generaltypes import Pipeline, StepValues, StepBlueprint
from backend.parameterTypes import ComplexPicker, Parameter, ParameterPicker, StaticParameter, InputOutputDefinition


class ParameterTransferObject:
    def __init__(self, name: str, type: str, description: str, defaultValue=None, picker: Optional['PickerObjectTransfer'] = None):
        self.name = name
        self.type = type
        self.description = description
        self.picker = picker
        self.defaultValue = defaultValue

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "defaultValue": self.defaultValue,
            "picker": self.picker.to_dict() if self.picker else None
        }


class PickerObjectTransfer:
    def __init__(self, name: str, outputType: str, values: Dict[str, object], innerParameters: List[ParameterTransferObject] = None):
        self.name = name
        self.outputType = outputType
        self.parameters = innerParameters
        self.values = values

    def to_dict(self):
        if self.parameters is not None and any(self.parameters):
            return {
                "name": self.name,
                "outputType": "complex",
                "parameters": [param.to_dict() for param in self.parameters]
            }
        else:
            return {
                "name": self.name,
                "outputType": self.outputType,
                "values": self.values
            }


class InOutDefTransferObject:
    def __init__(self, staticParameters: List[ParameterTransferObject],
                 dynamicParameters: List[ParameterTransferObject], outputParameters: List[ParameterTransferObject]):
        self.staticParameters = staticParameters
        self.dynamicParameters = dynamicParameters
        self.outputParameters = outputParameters

    def to_dict(self):
        return {
            "staticParameters": [param.to_dict() for param in self.staticParameters],
            "dynamicParameters": [param.to_dict() for param in self.dynamicParameters],
            "outputParameters": [param.to_dict() for param in self.outputParameters]
        }


class StepBlueprintTransferObject:
    def __init__(self, id: str, name: str, description: str, inOutDef: InOutDefTransferObject, tags: List[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.inOutDef = inOutDef
        self.tags = tags if tags else []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "inOutDef": self.inOutDef.to_dict(),
            "tags": self.tags
        }


class StepValuesTransferObject:
    def __init__(self, uniqueId: str, stepId: str, values: Dict[str, object]):
        self.uniqueId = uniqueId
        self.stepId = stepId
        self.values = values

    def to_dict(self):
        return {
            "uniqueId": self.uniqueId,
            "stepId": self.stepId,
            "values": self.values  # Assuming values are JSON-serializable already
        }


class PipelineTransferObject:
    def __init__(self, id: Optional[str] = None, name: Optional[str] = None, description: str = "",
                 steps: List[StepValuesTransferObject] = None, tags: List[str] = None):
        self.id = id if id else uuid.uuid4().hex
        self.name = name if name else f"Pipeline {self.id}"
        self.description = description
        self.steps = steps if steps else []
        self.tags = tags if tags is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "tags": self.tags
        }


# Example conversion functions (assuming instances of original classes are provided):
def convert_parameter_to_transfer(param: 'Parameter') -> ParameterTransferObject:
    picker = None
    if hasattr(param, "picker") and param.picker is not None:
        picker = convert_picker_to_transfer(param.picker)

    return ParameterTransferObject(name=param.name, type=str(param.type), defaultValue=param.defaultValue, description=param.description, picker=picker)


def convert_picker_to_transfer(picker: 'ParameterPicker') -> PickerObjectTransfer:
    parameters = None
    values = {}
    if isinstance(picker, ComplexPicker):
        parameters = [convert_parameter_to_transfer(p) for p in picker.inner]
    else:
        ignore = {"name", "outputType", "initializationParams", "default_values"}
        for k, v in vars(picker).items():
            if k in ignore:
                continue
            values[k] = v

    return PickerObjectTransfer(name=picker.name, outputType=str(picker.outputType), values=values, innerParameters=parameters)


def convert_in_out_def_to_transfer(in_out_def: 'InputOutputDefinition') -> InOutDefTransferObject:
    static_params = [convert_parameter_to_transfer(param) for param in in_out_def.inputs_static]
    dynamic_params = [convert_parameter_to_transfer(param) for param in in_out_def.inputs_dynamic]
    output_params = [convert_parameter_to_transfer(param) for param in in_out_def.outputs]
    return InOutDefTransferObject(staticParameters=static_params, dynamicParameters=dynamic_params,
                                  outputParameters=output_params)


def convert_step_blueprint_to_transfer(blueprint: 'StepBlueprint') -> StepBlueprintTransferObject:
    in_out_def_transfer = convert_in_out_def_to_transfer(blueprint.inOutDef)
    return StepBlueprintTransferObject(id=blueprint.stepId, name=blueprint.name, description=blueprint.description,
                                       inOutDef=in_out_def_transfer, tags=blueprint.tags)


def convert_step_values_to_transfer(step_values: 'StepValues') -> StepValuesTransferObject:
    return StepValuesTransferObject(uniqueId=step_values.uniqueId, stepId=step_values.stepId, values=step_values.values)


def convert_pipeline_to_transfer(pipeline: 'Pipeline') -> PipelineTransferObject:
    steps_transfer = [convert_step_values_to_transfer(step) for step in pipeline.steps]
    return PipelineTransferObject(id=pipeline.id, name=pipeline.name, description=pipeline.description,
                                  steps=steps_transfer, tags=pipeline.tags)
