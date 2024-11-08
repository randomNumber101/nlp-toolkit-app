from backend.generaltypes import StepOperation, Payload, StepOperationMapper
from backend.operations.DummyOperation import DummyOperation
from backend.parameterTypes import ParamType, ParameterPicker, Parameter, ListType
from backend.storage.parsing import ParameterTypeParser, ParameterPickerParser


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
    INT_LIST = ListType(INT)
    FLOAT_LIST = ListType(FLOAT)
    STRING_LIST = ListType(STRING)
    BOOL_LIST = ListType(BOOL)

    ALL = [INT, FLOAT, STRING, BOOL, INT_LIST, FLOAT_LIST, STRING_LIST, BOOL_LIST]
    MAP = {bt.name: bt for bt in ALL}

    @staticmethod
    def fromString(string):
        return BaseTypes.MAP[string]

    @staticmethod
    def isBaseType(string):
        return string in BaseTypes.MAP


'''
    Register StepOperations
'''
Register.OperationMapper.registerOperation(DummyOperation())  # Dummy Operation for Dummy Step

'''
    Register parameter value picker types for frontend.
'''

class TextField(ParameterPicker):
    def __init__(self, outputType):
        super(TextField, self).__init__("text_field", outputType=t, parameters=[])

# Text field picker as default
for t in BaseTypes.ALL:
    Register.ParamPickerParser.registerDefault(t, TextField(outputType=t))

class List(ParameterPicker):
    def __init__(self, defaultValue=0):
        listParams = [
            Parameter("possibilities", BaseTypes.STRING_LIST)
        ]
        self.default_value = defaultValue
        self.value = None
        super().__init__(name="list", outputType=BaseTypes.STRING, parameters=listParams)


Register.ParamPickerParser.registerParser("list", lambda kws: List().create_from_json(kws))


class Slider(ParameterPicker):
    def __init__(self):
        sliderParams = [
            Parameter("min", BaseTypes.FLOAT),
            Parameter("max", BaseTypes.FLOAT),
            Parameter("step", BaseTypes.FLOAT)
        ]
        super().__init__("slider", BaseTypes.FLOAT, sliderParams)


Register.ParamPickerParser.registerParser("slider", lambda kws: Slider().create_from_json(kws))
