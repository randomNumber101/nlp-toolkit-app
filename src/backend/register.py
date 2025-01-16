import typing
from typing import Dict, List, Tuple

from backend import utils
from backend.generaltypes import StepOperation, Payload, StepOperationMapper
from backend.operations.TextSimilarityOperation import TextSimilarityAnalysisOperation
from backend.parameterTypes import ParamType, ParameterPicker, Parameter, ListType
from backend.run.LogManager import LogManager
from backend.storage.parsing import ParameterTypeParser, ParameterPickerParser
import pandas as pd


from backend.operations.BertTopic import BertTopicOperation
from backend.operations.DataPreparationOperation import DataPreparationOperation
from backend.operations.DummyOperation import DummyOperation
from backend.operations.KeywordExtractionOperation import KeywordExtractionOperation
from backend.operations.SentimentAnalysisOperation import SentimentAnalysisOperation


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


class DataType(ParamType):
    Instances: Dict[Tuple[str], "DataType"] = {}

    def __init__(self, column_names: List[str]):
        self.column_names = column_names
        self._parse_to_df = utils.parseWildcardToDataframe
        column_names_str = ",".join(column_names)
        super().__init__(f"csv[{column_names_str}]", pd.DataFrame, parse=self._parse_to_df)

    def transformableInto(self, other):
        if not isinstance(other, DataType):
            return False

        my_cols = self.column_names
        other_cols = set(other.column_names)

        return len(other_cols.difference(my_cols)) == 0

    @staticmethod
    def getInstance(column_names: List[str]):
        key = tuple(column_names)
        if key not in DataType.Instances:
            DataType.Instances[key] = DataType(column_names)
        return DataType.Instances[key]


class TextField(ParameterPicker):
    def __init__(self, outputType):
        super(TextField, self).__init__("text_field", outputType=outputType, parameters=[])


class CheckBox(ParameterPicker):
    def __init__(self):
        super(CheckBox, self).__init__("checkbox", outputType=BaseTypes.BOOL, parameters=[])


class PossibilitiesPicker(ParameterPicker):
    def __init__(self, defaultValue=0):
        listParams = [
            Parameter("possibilities", BaseTypes.STRING_LIST)
        ]
        self.default_value = defaultValue
        self.value = None
        super().__init__(name="list", outputType=BaseTypes.STRING, parameters=listParams)


class ColumnPicker(ParameterPicker):
    def __init__(self, defaultValue=None):
        self.default_value = defaultValue
        self.value = None
        super().__init__(name="column_select", outputType=BaseTypes.STRING, parameters=[])


class Slider(ParameterPicker):
    def __init__(self):
        sliderParams = [
            Parameter("min", BaseTypes.FLOAT),
            Parameter("max", BaseTypes.FLOAT),
            Parameter("step", BaseTypes.FLOAT)
        ]
        super().__init__("slider", BaseTypes.FLOAT, sliderParams)


def registerClasses():
    '''
        Register StepOperations
    '''
    Register.OperationMapper.registerOperation("DummyStep", DummyOperation)  # Dummy Operation for Dummy Step
    Register.OperationMapper.registerOperation("BertTopic", BertTopicOperation)
    Register.OperationMapper.registerOperation("DataPreparation", DataPreparationOperation)
    Register.OperationMapper.registerOperation("SentimentAnalysis", SentimentAnalysisOperation)
    Register.OperationMapper.registerOperation("KeywordExtraction", KeywordExtractionOperation)
    Register.OperationMapper.registerOperation("TextSimilarityAnalysis", TextSimilarityAnalysisOperation)

    '''
        Register types
    '''
    for t in BaseTypes.ALL:
        Register.ParamTypeParser.registerType(t)

    Register.ParamTypeParser.registerGenericType("csv", DataType.getInstance)

    '''
        Register parameter value picker types for frontend.
    '''
    for t in BaseTypes.ALL:
        Register.ParamPickerParser.registerDefault(t, TextField(outputType=t))  # Text field picker as default
    Register.ParamPickerParser.registerDefault(BaseTypes.BOOL, CheckBox())  # Checkbox for bool values
    Register.ParamPickerParser.registerParser("text_field", lambda kws: TextField(BaseTypes.STRING))
    Register.ParamPickerParser.registerParser("list", lambda kws: PossibilitiesPicker().create_from_json(
        kws))  # Register list picker
    Register.ParamPickerParser.registerParser("column_select", lambda kws: ColumnPicker().create_from_json(kws))
    Register.ParamPickerParser.registerParser("slider",
                                              lambda kws: Slider().create_from_json(kws))  # Register value slider


registerClasses()
