from backend.generaltypes import StepOperation, Payload


class DummyOperation(StepOperation):
    def __init__(self):
        super().__init__("DummyStep")

    def run(self, payload: Payload):
        print("Dummy Operation was run!")
        payload.result = "Dummy operation"
        payload.visualization = {
            "type": "plaintext",
            "content": "This is the visualized result of Dummy Operation."
        }
