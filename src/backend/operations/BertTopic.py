import random
import time

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.generaltypes import StepOperation, Payload, FrontendNotifier, Config
from backend.transferObjects.visualization import SimpleTextViz, HTMLViz


## Needs to be registered in register.py
class BertTopicModelingOperation(StepOperation):

    def initialize(self, config: Config):
        pass

    def run(self, payload, notifier: FrontendNotifier) -> StepState:
        viz = HTMLViz("")

        return StepState.SUCCESS
