import webview
from webview import JavascriptException

from backend.transferObjects.eventTransferObjects import StepStatus, StepLogUpdate


class BackendEventApi:
    def sendStepLogs(self, stepLogs: StepLogUpdate):
        self.sendEvent("stepLogUpdate", stepLogs.to_json())

    def sendStepStatus(self, status: StepStatus):
        self.sendEvent("stepStatusUpdate", status.to_json())

    def sendEvent(self, event_name, data_json):
        if not webview.windows:
            raise RuntimeError("No window set.")


        try:
            webview.windows[0].evaluate_js(f"""
                        (function() {{
                            const event = new CustomEvent('{event_name}', {{ detail: {data_json} }});
                            window.dispatchEvent(event);
                        }})();
                    """)
        except JavascriptException as e:
            print("Error while trying to evaluate javascript:")
            print(f"""
                        (function() {{
                            const event = new CustomEvent('{event_name}', {{ detail: {data_json} }});
                            window.dispatchEvent(event);
                        }})();
                    """)
            print(repr(e))







