from typing import Callable, Dict, Any, List
from src.backend.parameterTypes import ParameterPicker, Parameter, ParamType, InputOutputDefinition, \
    StaticParameter, ComplexType, ComplexPicker
from src.backend.generaltypes import StepBlueprint, StepOperationMapper


# Utility functions to extract fields with optional default values
def get(obj: Dict[str, Any], field: str) -> Any:
    return obj[field]


def getOptional(obj: Dict[str, Any], field: str, default=None) -> Any:
    return obj.get(field, default)


class ParameterTypeParser:
    def __init__(self, parameterTypeList: List[ParamType] = None):
        self.typeMap = {}
        if parameterTypeList is not None:
            for pt in parameterTypeList:
                self.registerType(pt)

    def registerType(self, pt: ParamType):
        if pt.name not in self.typeMap:
            self.typeMap[pt.name] = pt.type

    def parse(self, name, strict=True):
        if name in self.typeMap:
            return self.typeMap[name]
        elif not strict:
            # Create CustomType
            print("Created custom type: " + name)
            customType = ParamType(name, None, parse=lambda x: x)
            self.registerType(customType)
            return customType
        raise LookupError(f"Type {name} is not registered. Disable strict mode to create new custom type.")

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


# Class to parse parameters, including complex types
class ParameterParser:
    def __init__(self, parameterTypeParser: ParameterTypeParser, pickerParser: ParameterPickerParser,
                 enforceStatic=False):
        self.typeParser = parameterTypeParser
        self.pickerParser = pickerParser
        self.enforceStatic = enforceStatic

    def parseParameterObject(self, name: str, param_obj: Dict[str, Any]) -> Parameter | StaticParameter:
        param_type_str = get(param_obj, "type")
        description = getOptional(param_obj, "description", "")
        default_value = getOptional(param_obj, "default")

        if not param_type_str == "complex":
            param_type = self.typeParser(param_type_str)
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

        del param_obj["type"]
        if "description" in param_obj:
            del param_obj["description"]
        if "default" in param_obj:
            del param_obj["default"]

        parameters = self.parseParameters(param_obj)
        if self.pickerParser is not None:
            picker = ComplexPicker(parameters)
            return StaticParameter(name, picker, description, default_value)
        else:
            paramType = ComplexType({p.name: p.type for p in parameters})
            return Parameter(name, paramType, description, default_value)

    def parseParameters(self, param_obj: Dict[str, Any]) -> List[Parameter | StaticParameter]:
        parameters = []
        for name, param_def in param_obj.items():
            if name == "type" and param_def == "complex":
                continue
            if isinstance(param_def, dict):
                parameters.append(self.parseParameterObject(name, param_def))
            elif isinstance(param_def, str):
                # Simple parameters without detailed definitions (e.g., "bool")
                param_type = self.typeParser(param_def)
                parameters.append(Parameter(name, param_type))
        return parameters


# Main class to parse StepBlueprint from JSON
class StepBlueprintParser:
    def __init__(self, pTypesParser: ParameterTypeParser, pPickerParser: ParameterPickerParser,
                 operationMapper: StepOperationMapper):
        self.staticParser = ParameterParser(pTypesParser, pPickerParser, enforceStatic=True)
        self.dynamicParser = ParameterParser(pTypesParser, pPickerParser, enforceStatic=False)
        self.operationMapper = operationMapper

    def parse(self, stepObject: Dict[str, Any]) -> StepBlueprint:
        # Extract basic step information
        step_id = get(stepObject, "id")
        name = get(stepObject, "name")
        description = getOptional(stepObject, "description", "")

        # Parse parameters, inputs, and outputs
        parameter_definitions = getOptional(stepObject, "parameters", {})
        parameters = self.staticParser.parseParameters(parameter_definitions)

        inputs = getOptional(stepObject, "inputs", {})
        outputs = getOptional(stepObject, "outputs", {})

        input_params = self.dynamicParser.parseParameters(inputs)
        output_params = self.dynamicParser.parseParameters(outputs)

        # Create InputOutputDefinition for this step
        in_out_def = InputOutputDefinition(staticInputs=parameters, dynamicInputs=input_params, outputs=output_params)

        # Instantiate the StepBlueprint
        operation = self.operationMapper.getOperation(step_id)  # Placeholder; actual implementation will vary
        step_blueprint = StepBlueprint(step_id, name, operation, description, inOutDef=in_out_def)

        return step_blueprint

    def __call__(self, stepObject: Dict[str, Any]) -> StepBlueprint:
        return self.parse(stepObject)