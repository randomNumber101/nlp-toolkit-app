import random
import time

from backend.transferObjects.eventTransferObjects import StepState, LogLevels
from backend.generaltypes import StepOperation, Payload, FrontendNotifier, Config
from backend.transferObjects.visualization import SimpleTextViz, HTMLViz


## Needs to be registered in register.py

dummy_html_visualization = """
<div style="font-family: Arial, sans-serif; padding: 20px;">
  <h3 style="color: #333; text-align: center;">Bar Chart Example</h3>
  <div style="display: flex; justify-content: space-around; align-items: flex-end; height: 200px; background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
    <div style="width: 50px; height: 120px; background: #4caf50; border-radius: 4px; text-align: center; color: white;">
      <span style="position: relative; top: -20px;">120</span>
    </div>
    <div style="width: 50px; height: 80px; background: #2196f3; border-radius: 4px; text-align: center; color: white;">
      <span style="position: relative; top: -20px;">80</span>
    </div>
    <div style="width: 50px; height: 150px; background: #f44336; border-radius: 4px; text-align: center; color: white;">
      <span style="position: relative; top: -20px;">150</span>
    </div>
    <div style="width: 50px; height: 100px; background: #ff9800; border-radius: 4px; text-align: center; color: white;">
      <span style="position: relative; top: -20px;">100</span>
    </div>
  </div>
  <div style="display: flex; justify-content: space-around; margin-top: 10px; color: #555;">
    <span>Category A</span>
    <span>Category B</span>
    <span>Category C</span>
    <span>Category D</span>
  </div>
</div>
"""



class DummyOperation(StepOperation):

    def initialize(self, config: Config):
        print("Loading config for DummyStep...")
        print(config)
        print(config["LLM config"])
        time.sleep(0.1)

    def run(self, payload: Payload, notifier: FrontendNotifier) -> StepState:
        notifier.log("Dummy Operation starting!")
        notifier.log("This operation is for tests only", LogLevels.WARN)
        for progress in range(0, 100, 10):
            notifier.sendStatus(StepState.RUNNING, progress)
            notifier.log(f"Mocked progress of {progress}/{100}")
            time.sleep(0.5)

        if random.random() > 0.9:
            if random.random() > 0.5:
                notifier.log("Error occurred during computation. (This is a test).", LogLevels.ERROR)
                return StepState.FAILED
            else:
                raise RuntimeError("Exception thrown during computation. (This is a test)")
        notifier.sendStatus(StepState.RUNNING, progress=100)
        payload.result = "Dummy operation"
        #payload.addVisualization(SimpleTextViz("Lorem ipsum dorem solomit. Dedum berit kolifat dere. Nemim dol krato sorem."))
        payload.addVisualization(HTMLViz(dummy_html_visualization))
        time.sleep(1)
        return StepState.SUCCESS
