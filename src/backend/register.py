from src.backend.generaltypes import StepOperation, Payload, StepOperationMapper
from src.backend.operations.DummyOperation import DummyOperation
from src.backend.parameterTypes import ParamType
from src.backend.storage.parsing import ParameterTypeParser, ParameterPickerParser


class Register:

    """
        For registering operations. (See operations/..)
    """
    OperationMapper = StepOperationMapper()

    '''
        For registering new types and type parsing
    '''
    ParamTypeParser = ParameterTypeParser([])

    '''
        Parser for ParameterPicker
    '''
    ParamPickerParser = ParameterPickerParser(ParamTypeParser)


class BaseTypes:
    INT = ParamType("int", int)
    FLOAT = ParamType("float", float)
    STRING = ParamType("string", str)
    BOOL = ParamType("bool", bool)

    ALL = [INT, FLOAT, STRING, BOOL]
    MAP = {bt.name: bt for bt in ALL}

    @staticmethod
    def fromString(string):
        return BaseTypes.MAP[string]

    @staticmethod
    def isBaseType(string):
        return string in BaseTypes.MAP



