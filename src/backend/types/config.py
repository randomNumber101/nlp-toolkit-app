import itertools
from typing import Any, List, Dict, Iterable, cast

from backend.types.params import Parameter, ComplexType


class Config(dict[str, Any]):
    def __init__(self, parameters: List[Parameter]):
        super().__init__()

        self.complexFields = set([])
        self.fields = {}
        for p in parameters:
            if p.type.name == "complex":
                pType = cast(ComplexType, p.type)
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
                complexValues = cast(Dict[str, object], vValue)
                self.fields[vName].setValues(complexValues)
            else:
                self.values[vName] = self.fields[vName].type.parse(vValue)


    def getMissingValues(self) -> Iterable[str]:
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

    def __iter__(self):
        complexVals = filter(lambda x: x in self.complexFields, self.fields)
        return itertools.chain(self.values, complexVals)

    def get_values(self):
        result = self.values
        for k, inner_config in self.fields.items():
            if inner_config not in self.complexFields:
                continue
            inner_config_dict = inner_config.get_values()
            result[k] = inner_config_dict
        return result



