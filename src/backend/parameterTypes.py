import copy
from abc import ABC, abstractmethod
from typing import Callable, Type, List, Dict, TypeVar, Generic, cast

T = TypeVar('T')


class ParamType(Generic[T]):

    def __init__(self, name, realType: Type = None, parse: Callable[[object], T] = None):
        from .register import Register

        self.name = name
        self.type = realType
        if realType is None and parse is None:
            raise RuntimeError(f"Cannot generate Type {self.name}. Specify type of parse function.")
        self.parse = (lambda x: cast(realType, x)) if parse is None else parse

        # Register this type
        Register.ParamTypeParser.registerType(self)

    def parse(self, value: object) -> T:
        return self.parse(value)

    def __repr__(self):
        return self.name.lower()


class ListType(ParamType):
    def __init__(self, innerType: ParamType):
        self.innerType = innerType
        self._parse_list = lambda list_val: list([innerType.parse(x) for x in list_val])

        super().__init__(f"list[{innerType.name}]", List[innerType.type], parse=self._parse_list)


class ComplexType(ParamType):
    def __init__(self, innerTypes: Dict[str, ParamType]):
        self.innerTypes = innerTypes

        def parse(obj: Dict[str, object]):
            return {key: paraType.parse(obj[key]) for key, paraType in innerTypes.items()}

        super().__init__("Complex", Dict[str, object], parse=parse)


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
                raise ValueError(f"Cannot create picker form obj {obj}. Field {p.name} is missing.")
            kwargs[p.name] = p.type.parse(values[p.name])

        self.initialize(**kwargs)
        return self


class ComplexPicker(ParameterPicker):
    def __init__(self, innerParams: List["Parameter"], name="complex"):
        self.inner = innerParams
        outputType = ComplexType({param.name: param.type for param in innerParams})
        super().__init__(name=name, outputType=outputType, parameters=[])


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
