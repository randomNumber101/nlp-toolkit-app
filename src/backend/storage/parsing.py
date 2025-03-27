import re
import typing
from typing import Callable, Dict, Any, List

from backend.types.blueprint import StepBlueprint, InputOutputDefinition, StepValues
from backend.types.operation import StepOperationMapper
from backend.types.params import StaticParameter, Parameter
from backend.types.pickers import ParamType, ComplexType, ParameterPicker, ComplexPicker, ComplexListPicker
import uuid

from backend.types.pipeline import Pipeline


# Utility functions to extract fields with optional default values
def get(obj: Dict[str, Any], field: str) -> Any:
    return obj[field]


def getOptional(obj: Dict[str, Any], field: str, default=None) -> Any:
    return obj.get(field, default)


class ParameterTypeParser:
    def __init__(self, parameterTypeList: List[ParamType] = None):
        self.typeMap = {}
        self.genTypeMap = {}
        if parameterTypeList is not None:
            for pt in parameterTypeList:
                self.registerType(pt)

    def registerType(self, pt: ParamType):
        if pt.name not in self.typeMap:
            self.typeMap[pt.name] = pt

    def registerGenericType(self, name: str, initializer: Callable[[List[str]], ParamType]):
        self.genTypeMap[name.lower()] = initializer

    def parse(self, typeString : str, strict=True):
        if strict is None:
            strict = True

        typeString = typeString.lower()

        match = re.search(r"(\w*)(\[(\w+(,\w+)*)\])?", typeString)
        typeName = match.group(1)
        typeArgs = match.group(3).split(sep=",") if match.lastindex > 2 else None

        if typeArgs or typeName in self.genTypeMap:
            if not typeArgs:
                typeArgs = []
            typObj = self.genTypeMap[typeName](typeArgs)
            return typObj

        if typeString in self.typeMap: # Edge case when generic type is not registered. TODO: Rewrite List type to generate types dynamically
            typeName = typeString

        if typeName in self.typeMap:
            typeObj = self.typeMap[typeName]
            return typeObj


        elif not strict:
            # Create CustomType
            print("Created custom type: " + typeName)
            customType = ParamType(typeName, None, parse=lambda x: x)
            self.registerType(customType)
            return customType
        raise LookupError(f"Type {typeName} is not registered. Disable strict mode to create new custom type.")

    def __call__(self, name, strict=True):
        return self.parse(name, strict)


# Class to parse parameter pickers
class ParameterPickerParser:
    def __init__(self, typeParser: ParameterTypeParser):
        self.typeParser = typeParser
        self.defaultPickers: Dict[ParamType, ParameterPicker] = {}
        self.parseOps: Dict[str, Callable[[Dict[str, Any]], ParameterPicker]] = {}

    def registerParser(self, name: str, parseOperation: Callable[[Dict[str, Any]], ParameterPicker]):
        if name == "complex":
            raise ValueError("Cannot register parser for complex pickers.")
        self.parseOps[name] = parseOperation

    def registerDefault(self, paramType: ParamType, defaultPicker: ParameterPicker):
        self.defaultPickers[paramType] = defaultPicker

    def parse(self, obj: Any) -> ParameterPicker:
        if isinstance(obj, str):
            obj = self.typeParser(obj)
            if obj in self.defaultPickers:
                return self.defaultPickers[obj]
            raise NotImplementedError(f"No Parameter Picker registered for base type {obj}.")
        elif "type" in obj:
            paraType = obj["type"]
            if paraType in self.parseOps:
                return self.parseOps[paraType](obj)
            raise NotImplementedError(f"No Parameter Picker registered for type {paraType}.")

        raise ValueError(f"Cannot parse ParameterPicker for object: {obj}")

    def useDefault(self, paramType: ParamType) -> ParameterPicker:
        if paramType in self.defaultPickers:
            return self.defaultPickers[paramType]
        else:
            raise NotImplementedError(f"No default picker installed for type {paramType}")


# Class to parse types, including complex types
class ParameterParser:
    def __init__(self, parameterTypeParser: ParameterTypeParser, pickerParser: ParameterPickerParser,
                 enforceStatic=False, strictTyping=True):
        self.typeParser = parameterTypeParser
        self.pickerParser = pickerParser
        self.enforceStatic = enforceStatic
        self.strictTyping = strictTyping

    def parseParameterObject(self, name: str, param_obj: Dict[str, Any]) -> Parameter | StaticParameter:
        param_type_str = get(param_obj, "type")
        description = getOptional(param_obj, "description", "")
        default_value = getOptional(param_obj, "default")

        if param_type_str == "complex":
            # For Complex (composite) types, parse residual key-values as types.

            if "inner_parameters" not in param_obj:
                print(param_obj)
                raise SyntaxError(f"Complex type {name} requires inner types.")

            parameters = self.parseParameters(param_obj["inner_parameters"])
            if self.pickerParser is not None:
                picker = ComplexPicker(parameters)
                complexType = typing.cast(ComplexType, picker.outputType)
                default_values = complexType.getDefaults()
                return StaticParameter(name, picker, description, default_values)
            else:
                complexType = ComplexType(parameters)
                return Parameter(name, complexType, description, complexType.getDefaults())

        elif param_type_str == "complex_list":

            if "inner_parameters" not in param_obj:
                print(param_obj)
                raise SyntaxError(f"Complex type {name} requires inner types.")

            inner_params = self.parseParameters(get(param_obj, "inner_parameters"))
            max_list_length = getOptional(param_obj, "max_length", None)
            entry_format = getOptional(param_obj, "entry_format", "<value>")
            loadable_from_file = getOptional(param_obj, "loadable_from_file", False)

            if self.pickerParser is None:
                raise SyntaxError("Complex List ist not allowed as a type for Dynamic types.")

            picker = ComplexListPicker(inner_params, max_length=max_list_length, entry_format=entry_format, loadable_from_file=loadable_from_file)
            return StaticParameter(name, picker, description, [])





        else:
            param_type = self.typeParser(param_type_str, strict=self.strictTyping)
            picker_obj = getOptional(param_obj, "input")

            if self.enforceStatic:
                if picker_obj:
                    picker = self.pickerParser.parse(picker_obj)
                else:
                    picker = self.pickerParser.useDefault(param_type)


                return StaticParameter(name, picker, description, default_value)
            elif picker_obj:
                picker = self.pickerParser.parse(picker_obj)
                return StaticParameter(name, picker, description, default_value)
            else:
                return Parameter(name, param_type, description, default_value)




    def parseParameters(self, param_obj: Dict[str, Any]) -> List[Parameter | StaticParameter]:
        parameters = []
        for name, param_def in param_obj.items():
            if name == "type" and param_def == "complex":
                continue
            if isinstance(param_def, dict):
                parameters.append(self.parseParameterObject(name, param_def))
            elif isinstance(param_def, str):
                # Simple types without detailed definitions (e.g., "bool")
                param_type = self.typeParser(param_def, strict=self.strictTyping)
                try:
                    picker = self.pickerParser.useDefault(param_type)
                    parameter = StaticParameter(name, picker)
                except NotImplementedError as e:
                    if self.enforceStatic:
                        raise e
                    parameter = Parameter(name, param_type)
                parameters.append(parameter)
        return parameters


# Main class to parse StepBlueprint from JSON
class StepBlueprintParser:
    def __init__(self, pTypesParser: ParameterTypeParser, pPickerParser: ParameterPickerParser,
                 operationMapper: StepOperationMapper):
        self.staticParser = ParameterParser(pTypesParser, pPickerParser, enforceStatic=True)
        self.dynamicParser = ParameterParser(pTypesParser, pPickerParser, enforceStatic=False, strictTyping=False)
        self.operationMapper = operationMapper

    def parse(self, stepObject: Dict[str, Any]) -> StepBlueprint:
        # Extract basic step information
        step_id = get(stepObject, "id")
        name = get(stepObject, "name")
        description = getOptional(stepObject, "description", "")
        information = getOptional(stepObject, "information", None)
        tags = getOptional(stepObject, "tags", [])

        # Parse types, inputs, and outputs
        parameter_definitions = getOptional(stepObject, "parameters", {})
        parameters = self.staticParser.parseParameters(parameter_definitions)

        inputs = getOptional(stepObject, "inputs", {})
        outputs = getOptional(stepObject, "outputs", {})

        input_params = self.dynamicParser.parseParameters(inputs)
        output_params = self.dynamicParser.parseParameters(outputs)

        # Create InputOutputDefinition for this step
        in_out_def = InputOutputDefinition(staticInputs=parameters, dynamicInputs=input_params, outputs=output_params)

        # Instantiate the StepBlueprint
        operation = self.operationMapper.getOperation(step_id)
        step_blueprint = StepBlueprint(step_id, name, operation, description,  information=information, inOutDef=in_out_def, tags=tags)

        return step_blueprint

    def __call__(self, stepObject: Dict[str, Any]) -> StepBlueprint:
        return self.parse(stepObject)


class PipelineParser:
    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> Pipeline:
        """
        Parses a JSON object into a Pipeline instance.
        """
        # Extract basic pipeline details
        pipeline_id = json_data.get("id", str(uuid.uuid4()))
        name = json_data.get("name", f"Pipeline {pipeline_id}")
        description = json_data.get("description", "")
        information = json_data.get("information", None)

        # Parse steps
        steps = []
        for step_data in json_data.get("steps", []):
            uniqueId = step_data.get("uniqueId", str(uuid.uuid4()))
            step_id = step_data["stepId"]
            values = step_data.get("values", {})
            step = StepValues(uniqueId, step_id, values)
            steps.append(step)

        tags = json_data.get("tags", [])

        # Create and return Pipeline instance
        return Pipeline(id=pipeline_id, name=name, description=description, information=information, steps=steps, tags=tags)

    @staticmethod
    def to_json(pipeline: Pipeline) -> Dict[str, Any]:
        """
        Converts a Pipeline instance into a JSON-serializable dictionary.
        """
        # Create JSON-compatible dictionary from Pipeline
        pipeline_dict = {
            "id": pipeline.id,
            "name": pipeline.name,
            "description": pipeline.description,
            "steps": [
                {
                    "stepId": step.stepId,
                    "values": step.values
                }
                for step in pipeline.steps
            ],
            "tags": pipeline.tags
        }
        return pipeline_dict
