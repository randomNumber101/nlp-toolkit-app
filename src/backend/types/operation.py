import time
import traceback
from abc import ABC, abstractmethod
from collections import Counter

from pydantic import typing

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.types.config import Config
from backend.types.frontendNotifier import FrontendNotifier, CellNotifierWrapper


class StepOperation(ABC):
    def __init__(self, config: Config, frontendNotifier: FrontendNotifier = None):
        self.initialize(config, frontendNotifier)

    @abstractmethod
    def initialize(self, config: Config, frontendNotifier: FrontendNotifier):
        pass

    @abstractmethod
    def run(self, payload, notifier: FrontendNotifier) -> StepState:
        pass

    def __call__(self, payload, notifier: FrontendNotifier) -> StepState:
        return self.run(payload, notifier)


class ParallelizableOperation(StepOperation, ABC):
    def __init__(self, config, notifier):
        super(ParallelizableOperation, self).__init__(config, notifier)
        self.config = config
        # Assumes the configuration defines an "input column"
        self.input_column = self.config.get("input column", "text")
        if isinstance(self.input_column, list):
            self.input_column = self.input_column[0]

    @abstractmethod
    def single_cell_operation(self, notifier, payload, cell_value):
        """
        Process one cell.
        Must return a tuple or list of outputs; one for each output column.
        """
        pass

    @abstractmethod
    def getColumnNames(self) -> list:
        """
        Return a list of column names for the outputs.
        """
        pass

    def run(self, payload, notifier) -> 'StepState':
        import pandas as pd

        start_time = time.time()
        data: pd.DataFrame = payload.data
        counter = Counter({"success": 0, "failed": 0})
        num_cells = len(data[self.input_column])
        output_columns = self.getColumnNames()

        cell_index = 0

        def transform(cell_value):
            nonlocal cell_index
            cellNotifier = CellNotifierWrapper(notifier, counter, cell_index, num_cells)
            cell_index += 1
            try:
                result = self.single_cell_operation(cellNotifier, payload, cell_value)
                if not isinstance(result, (list, tuple)):
                    raise ValueError("single_cell_operation must return a list or tuple.")
                if len(result) != len(output_columns):
                    raise ValueError(
                        f"Expected {len(output_columns)} outputs but got {len(result)}."
                    )
                counter["success"] += 1
                return result
            except Exception as e:
                traceback_str = traceback.format_exc()
                notifier.log(traceback_str, LogLevels.ERROR)
                cellNotifier.log(f"Error processing cell {cell_index}: {e}", LogLevels.ERROR)
                counter["failed"] += 1
                # Return a tuple with None for each expected output.
                return tuple([None] * len(output_columns))

        results = data[self.input_column].apply(transform)
        result_df = pd.DataFrame(results.tolist(), index=data.index, columns=output_columns)

        for col in output_columns:
            data[col] = result_df[col]

        end_time = time.time()
        notifier.log(f"Total processing time: {end_time - start_time:.2f} seconds", LogLevels.INFO)
        if counter["failed"] > 0:
            notifier.log(f"{counter['failed']} of {num_cells} failed. Data may be incomplete.", LogLevels.ERROR)
            return StepState.FAILED

        payload.data = data
        return StepState.SUCCESS


# The new subclass that reuses ParallelizableOperation for single‑value outputs.
class ParallelizableTextOperation(ParallelizableOperation, ABC):
    def __init__(self, config, notifier):
        self.config = config
        self.input_column = self.config.get("input column", "text")
        if isinstance(self.input_column, list):
            self.input_column = self.input_column[0]

        # Determine output column
        self.output_column = self.config.get("output column", None)
        if self.output_column == "" or self.output_column is None:
            self.output_column = self.input_column
        super().__init__(config, notifier)

    @abstractmethod
    def single_cell_operation(self, notifier, payload, text: str) -> str:
        """
        Process one cell and return a single string as output.
        """
        pass

    def getColumnNames(self) -> list:
        # For single output operations, simply return one-element list.
        return [self.output_column]

    def run(self, payload, notifier) -> 'StepState':
        start_time = time.time()

        # Save the original operation.
        original_operation = self.single_cell_operation

        def wrapper(cell_notifier, payload, text: str):
            result = original_operation(cell_notifier, payload, text)
            return (result,)  # Wrap it in a tuple

        # Swap in our wrapper so that the parent run method sees tuple outputs.
        self.single_cell_operation = wrapper
        state = super().run(payload, notifier)
        self.single_cell_operation = original_operation

        end_time = time.time()
        notifier.log(f"Total processing time: {end_time - start_time:.2f} seconds", LogLevels.INFO)
        return state


class StepOperationMapper:

    def __init__(self):
        self.operations = {}

    def registerOperation(self, stepId: str, operation: typing.Type[StepOperation]):
        self.operations[stepId] = operation

    def getOperation(self, stepId) -> typing.Type[StepOperation]:
        if stepId in self.operations:
            return self.operations[stepId]
        raise NotImplementedError(
            f"No registered operation found for Step Id {stepId}. Create new or register operation.")