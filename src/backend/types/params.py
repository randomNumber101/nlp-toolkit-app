from typing import Generic, TypeVar, Type, Callable, cast, Dict, List

from pydantic import typing

T = TypeVar('T')


class ParamType(Generic[T]):

    def __init__(self, name, realType: Type = None, parse: Callable[[object], T] = None, defaultValue=None):
        self.name = name
        self.type = realType
        self.defaultValue = defaultValue

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


class Parameter:
    def __init__(self, name, paraType: ParamType, description="", defaultValue=None):
        self.picker = None
        self.name = name
        self.type = paraType
        self.description = description

        if defaultValue is None:
            defaultValue = paraType.defaultValue

        self.defaultValue = defaultValue


class StaticParameter(Parameter):
    def __init__(self, name, picker: "ParameterPicker", description="", defaultValue=None):
        super().__init__(name, picker.outputType, description, defaultValue)
        self.picker = picker