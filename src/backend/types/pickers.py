import copy
import typing
from abc import ABC
from typing import List, Dict

from backend.types.params import Parameter, ParamType, ComplexType, ListType


class ParameterPicker(ABC):
    def __init__(self, name: str, outputType: ParamType, parameters: List["Parameter"], default_values=None):
        self.initializationParams = parameters
        self.name = name
        self.outputType = outputType
        self.default_values = default_values if default_values else {}

    def initialize(self, **kwargs):
        if "outputType" in kwargs:
            from ..register import Register
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
    def __init__(self, innerParams: List["Parameter"]):
        self.inner = innerParams
        outputType = ComplexType(innerParams)
        super().__init__(name="complex", outputType=outputType, parameters=[])


class ComplexListPicker(ParameterPicker):
    def __init__(self, innerParams: List["Parameter"], max_length=50, entry_format="<value>"):
        self.inner = innerParams
        self.max_length = max_length  # Maximum number of elements in the list
        self.entry_format = entry_format  # The format of the entries in the list <#> will be replaced by the index, <value> by first inner param value
        if len(innerParams) == 1:
            innerType = innerParams[0].type
        else:
            innerType = ComplexType(innerParams)
        outputType = ListType(innerType)
        super().__init__(name="complex_list", outputType=outputType, parameters=[])
