import random
import time

from backend.transferObjects.eventTransferObjects import StepState
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
        notifier.sendStatus(StepState.RUNNING, progress=0)
        time.sleep(1)
        notifier.log("Executed first calculcation.")
        notifier.sendStatus(StepState.RUNNING, progress=25)
        time.sleep(1)
        notifier.log("Executed 2nd calculcation.")
        notifier.sendStatus(StepState.RUNNING, progress=75)
        time.sleep(1)
        notifier.log("Executed last calculcation.")
        if random.random() > 0.9:
            if random.random() > 0.5:
                notifier.log("Error occurred during computation.")
                return StepState.FAILED
            else:
                raise RuntimeError("Exception thrown during computation.")
        notifier.sendStatus(StepState.RUNNING, progress=100)
        payload.result = "Dummy operation"
        payload.addVisualization(SimpleTextViz("Lorem ipsum dorem solomit. Dedum berit kolifat dere. Nemim dol krato sorem."))
        time.sleep(0.05)
        notifier.sendStatus(StepState.SUCCESS, progress=100)
        return StepState.SUCCESS
