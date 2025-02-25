import copy
import typing
from abc import ABC, abstractmethod
from typing import Callable, Type, List, Dict, TypeVar, Generic, cast

T = TypeVar('T')


class ParamType(Generic[T]):

    def __init__(self, name, realType: Type = None, parse: Callable[[object], T] = None):
        from .register import Register

        self.name = name
        self.type = realType

        if parse is not None:
            self.parse = parse
        elif realType is not None:
            self.parse = lambda value: cast(realType, value)
        else:
            self.parse = lambda x: x  # Leave value as is

    def parse(self, value: object) -> T:
        return self.parse(value)

    def __repr__(self):
        return self.name.lower()

    def transformableInto(self, other):
        return self.__eq__(other)


class ListType(ParamType):
    def __init__(self, innerType: ParamType = None):
        self.innerType = innerType
        self._parse_list = lambda list_val: list([innerType.parse(x) for x in list_val])
        super().__init__(f"list[{innerType.name}]", List[innerType.type], parse=self._parse_list)


class ComplexType(ParamType):
    def __init__(self, innerParams: List["Parameter"]):
        self.innerParams = innerParams

        def parse(obj: Dict[str, object]):
            return {p.name: p.type.parse(obj[p.name]) for p in innerParams}

        super().__init__("complex", Dict[str, object], parse=parse)

    def getDefaults(self):
        defaults = {}
        for p in self.innerParams:
            if p.type.name != "complex":
                if p.defaultValue:
                    defaults[p.name] = p.defaultValue
            else:
                complexType = typing.cast(ComplexType, p.type)
                defaults[p.name] = complexType.getDefaults()
        return defaults


# Contains information on how to configure the parameter for the frontend
class ParameterPicker(ABC):
    def __init__(self, name: str, outputType: ParamType, parameters: List["Parameter"], default_values=None):
        self.initializationParams = parameters
        self.name = name
        self.outputType = outputType
        self.default_values = default_values if default_values else {}

    def initialize(self, **kwargs):
        if "outputType" in kwargs:
            from register import Register
            outputType = Register.ParamTypeParser.parse(kwargs["outputType"])
            self.outputType = outputType
            del kwargs["outputType"]

        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def create_from_json(self, obj: Dict[str, object]):
        values = copy.deepcopy(self.default_values)
        values.update(obj)
        kwargs = {}
        for p in self.initializationParams:
            if p.name not in values:
                raise ValueError(f"Cannot create picker from obj {obj}. Field {p.name} is missing.")
            kwargs[p.name] = p.type.parse(values[p.name])

        self.initialize(**kwargs)
        return self


class ComplexPicker(ParameterPicker):
    def __init__(self, innerParams: List["Parameter"], name="complex"):
        self.inner = innerParams
        outputType = ComplexType(innerParams)
        super().__init__(name=name, outputType=outputType, parameters=[])


class ListPicker(ParameterPicker):
    def __init__(self, innerParam: "Parameter" = None, name="list_picker"):
        self.innerParam = innerParam
        outputType = ListType(innerParam.type) if innerParam else None
        super().__init__(name=name, outputType=outputType, parameters=[])
        self.value = None


class Parameter:
    def __init__(self, name, paraType: ParamType, description="", defaultValue=None):
        self.picker = None
        self.name = name
        self.type = paraType
        self.description = description
        self.defaultValue = defaultValue


class StaticParameter(Parameter):
    def __init__(self, name, picker: ParameterPicker, description="", defaultValue=None):
        super().__init__(name, picker.outputType, description, defaultValue)
        self.picker = picker


class InputOutputDefinition:
    def __init__(self, staticInputs: List[StaticParameter], dynamicInputs: List[Parameter], outputs: List[Parameter]):
        self.inputs_static = staticInputs
        self.inputs_dynamic = dynamicInputs
        self.outputs = outputs
