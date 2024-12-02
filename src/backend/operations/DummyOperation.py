import random
import time

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.generaltypes import StepOperation, Payload, FrontendNotifier, Config
from backend.transferObjects.visualization import SimpleTextViz


## Needs to be registered in register.py
class DummyOperation(StepOperation):

    def initialize(self, config: Config):
        print("Loading config for DummyStep...")
        print(config)
        print(config["LLM config"])
        time.sleep(0.1)

    def run(self, payload: Payload, notifier: FrontendNotifier) -> StepState:
        notifier.log("Dummy Operation starting!")
        notifier.log("This operation is for tests only", LogLevels.WARN)
        notifier.sendStatus(StepState.RUNNING, progress=0)
        time.sleep(1.5)
        notifier.log("Executed first calculcation.")
        notifier.sendStatus(StepState.RUNNING, progress=25)
        time.sleep(1.5)
        notifier.log("Executed 2nd calculcation.")
        notifier.sendStatus(StepState.RUNNING, progress=75)
        time.sleep(1.5)
        notifier.log("Executed last calculcation.")
        if random.random() > 0.9:
            if random.random() > 0.5:
                notifier.log("Error occurred during computation. (This is a test).")
                return StepState.FAILED
            else:
                raise RuntimeError("Exception thrown during computation. (This is a test)")
        notifier.sendStatus(StepState.RUNNING, progress=100)
        payload.result = "Dummy operation"
        payload.addVisualization(SimpleTextViz("Lorem ipsum dorem solomit. Dedum berit kolifat dere. Nemim dol krato sorem."))
        time.sleep(1)
        return StepState.SUCCESS
