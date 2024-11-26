import time

from backend.events.eventTransferObjects import StepState
from backend.generaltypes import StepOperation, Payload, FrontendNotifier


## Needs to be registered in register.py
class DummyOperation(StepOperation):
    def __init__(self, logger):
        super().__init__("DummyStep", logger)

    def run(self, payload: Payload, notifier: FrontendNotifier):
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
        notifier.sendStatus(StepState.RUNNING, progress=100)
        payload.result = "Dummy operation"
        payload.visualization = {
            "type": "plaintext",
            "content": "This is the visualized result of Dummy Operation."
        }
        time.sleep(0.05)
        notifier.sendStatus(StepState.SUCCESS, progress=100)
